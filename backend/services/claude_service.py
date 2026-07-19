"""
Wrapper around the Anthropic API. Handles:
- Reading an uploaded photo/PDF/docx of a textbook lesson
- Asking Claude to produce STRICT JSON matching our lesson-plan / slide /
  test / curriculum schemas (in Khmer), so the frontend + docx exporter
  can render it reliably.
"""
import os
import json
import base64
import mimetypes
from anthropic import Anthropic
from flask import current_app

METHOD_LABELS = {
    "inquiry": "វិធីសាស្ត្របែបរិះរក (Inquiry-Based)",
    "bloom": "វិធីសាស្ត្របែប Bloom's Taxonomy",
    "student_centered": "វិធីសាស្ត្របែបសិស្សមជ្ឈមណ្ឌល (Student-Centered)",
}

ANTHROPIC_MODEL = "claude-sonnet-4-6"
GEMINI_MODEL = "gemini-3.5-flash"


def _provider():
    """Decide which AI provider to use: explicit AI_PROVIDER env, else whichever key is set."""
    configured = current_app.config.get("AI_PROVIDER") or os.environ.get("AI_PROVIDER", "")
    configured = configured.strip().lower()
    if configured in ("anthropic", "gemini"):
        return configured

    if current_app.config.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    return "anthropic"


def _anthropic_client():
    api_key = current_app.config.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY មិនត្រូវបានកំណត់នៅក្នុងឯកសារ .env ទេ")
    return Anthropic(api_key=api_key)


def _gemini_client():
    from google import genai

    api_key = current_app.config.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY មិនត្រូវបានកំណត់នៅក្នុងឯកសារ .env ទេ")
    return genai.Client(api_key=api_key)


def _file_to_content_block(filepath):
    """Turns an uploaded image or PDF into an Anthropic content block."""
    mime, _ = mimetypes.guess_type(filepath)
    with open(filepath, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    if mime == "application/pdf":
        return {
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": b64},
        }
    # default to image
    mime = mime or "image/jpeg"
    return {
        "type": "image",
        "source": {"type": "base64", "media_type": mime, "data": b64},
    }


def _file_to_gemini_part(filepath):
    """Turns an uploaded image or PDF into a google-genai Part."""
    from google.genai import types

    mime, _ = mimetypes.guess_type(filepath)
    mime = mime or "application/octet-stream"
    with open(filepath, "rb") as f:
        raw = f.read()
    return types.Part.from_bytes(data=raw, mime_type=mime)


def _extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


LESSON_PLAN_SCHEMA_HINT = """
{
  "date": "ថ្ងៃខែឆ្នាំបង្រៀន",
  "grade": "ថ្នាក់ទី",
  "subject": "មុខវិជ្ជា",
  "chapter": "ជំពូកទី ... (ចំណងជើងជំពូក)",
  "lesson": "មេរៀនទី ... (ចំណងជើងមេរៀន)",
  "topic": "សិក្សាអំពី ...",
  "duration": "រយៈពេល ០១ ម៉ោង",
  "approach": "គ្រូមជ្ឈមណ្ឌល និង សិស្សមជ្ឈមណ្ឌល",
  "method": "ឈ្មោះវិធីសាស្ត្របង្រៀនដែលបានជ្រើសរើស",
  "objectives": {
    "knowledge": "វិជ្ជាទស្សន៍៖ ...",
    "skills": "បំណិន៖ ...",
    "attitude": "ចរិយា៖ ..."
  },
  "materials": {
    "documents": "ឯកសារយោង (សៀវភៅ, ជំពូក, ទំព័រ)",
    "tools": "ឧបករណ៍ (Computer, LCD Projector ...)"
  },
  "activities": [
    {
      "step_title": "១. រដ្ឋបាលថ្នាក់រៀន",
      "time": "៥ នាទី",
      "teacher_activity": "...",
      "content": "...",
      "student_activity": "..."
    },
    {
      "step_title": "២. រំលឹកមេរៀនចាស់ និងសំណួរបំបាត់",
      "time": "៥ នាទី",
      "teacher_activity": "...",
      "content": "...",
      "student_activity": "..."
    },
    {
      "step_title": "៣. មេរៀនប្រចាំថ្ងៃ",
      "time": "៣៥ នាទី",
      "teacher_activity": "...",
      "content": "ខ្លឹមសារពេញលេញនៃមេរៀន បែងចែកជាចំណុចរង",
      "student_activity": "..."
    },
    {
      "step_title": "៤. ពង្រឹងពុទ្ធិ",
      "time": "១០ នាទី",
      "teacher_activity": "សំណួរតេស្ត/ព្រឹងភាព",
      "content": "...",
      "student_activity": "..."
    },
    {
      "step_title": "៥. កិច្ចការផ្ទះ និងបណ្ដាំនិយាយ",
      "time": "៥ នាទី",
      "teacher_activity": "...",
      "content": "កិច្ចការផ្ទះ",
      "student_activity": "..."
    }
  ]
}
"""

SLIDE_SCHEMA_HINT = """
{
  "title": "ចំណងជើងធំសម្រាប់ស្លាយទាំងមូល (ឧ. មេរៀនទី២៖ ...)",
  "subtitle": "ជំពូក/ថ្នាក់ (ឧ. ជំពូកទី១៖ ... ថ្នាក់ទី១០)",
  "footer_left": "អត្ថបទតូចលើក្បាលទំព័រខាងឆ្វេង (ឧ. ក្រសួងអប់រំ យុវជន និងកីឡា)",
  "slides": [
    {
      "type": "cover",
      "section_label": "GRADE 10 · CHAPTER 1",
      "heading": "ចំណងជើងគម្រប",
      "subheading": "ខ្សែបន្ទាត់រង"
    },
    {
      "type": "bullets",
      "section_label": "រំលឹងបំណង",
      "heading": "ចំណងជើងស្លាយ",
      "items": [
        {"title": "ពាក្យគន្លឹះ", "desc": "ការពន្យល់ខ្លីមួយឃ្លា"}
      ]
    },
    {
      "type": "two_column",
      "section_label": "ការអនុវត្ត",
      "heading": "ចំណងជើងស្លាយ",
      "paragraphs": ["កថាខណ្ឌទី១...", "កថាខណ្ឌទី២..."],
      "stat_number": "60%",
      "stat_label": "ស្លាកខ្លីពណ៌នាលេខស្ថិតិ (ទុកទទេ បើគ្មាន)",
      "image_caption": "ពាក្យខ្លីសម្រាប់រូបភាព/គំនូសតាង (ទុកទទេ បើគ្មាន)"
    },
    {
      "type": "cards",
      "section_label": "ដំណើរការ",
      "heading": "ចំណងជើងស្លាយ",
      "cards": [
        {"icon": "🎯", "title": "ចំណងជើងកាតតូច", "desc": "ការពន្យល់ខ្លី"}
      ]
    },
    {
      "type": "timeline",
      "section_label": "បដិវត្តន៍",
      "heading": "ចំណងជើងស្លាយ",
      "stages": [
        {"title": "1st Stage", "subtitle": "ចំណងជើងរង", "desc": "ការពន្យល់ខ្លី"}
      ]
    },
    {
      "type": "table",
      "section_label": "ទិន្នន័យ",
      "heading": "ចំណងជើងស្លាយ",
      "columns": ["ជួរឈរទី១", "ជួរឈរទី២", "ជួរឈរទី៣"],
      "rows": [["ក", "ខ", "គ"]]
    },
    {
      "type": "compare",
      "section_label": "ប្រៀបធៀប",
      "heading": "ចំណងជើងស្លាយ",
      "left": {"icon": "⚙️", "title": "ចំណងជើងឆ្វេង", "bullets": ["ចំណុចទី១", "ចំណុចទី២"]},
      "right": {"icon": "💾", "title": "ចំណងជើងស្តាំ", "bullets": ["ចំណុចទី១", "ចំណុចទី២"]}
    },
    {
      "type": "section",
      "section_label": "ចាប់ផ្តើម",
      "heading": "សំណួរធំកណ្តាលអេក្រង់",
      "subheading": "ខ្សែបន្ទាត់រងខ្លី"
    },
    {
      "type": "closing",
      "section_label": "សរុប",
      "heading": "សំណួរពិនិត្យឡើងវិញ (Review)",
      "questions": ["សំណួរទី១...", "សំណួរទី២..."],
      "contact": "www.moeys.gov.kh (ឬទុកទទេ)"
    }
  ]
}
"""

TEST_SCHEMA_HINT = """
{
  "title": "តេស្តស្តង់ដារ - មុខវិជ្ជា/ថ្នាក់/មេរៀន",
  "instructions": "សេចក្តីណែនាំធ្វើតេស្ត",
  "duration": "រយៈពេលធ្វើតេស្ត",
  "sections": [
    {
      "section_title": "ផ្នែកទី១៖ ជម្រើសពហុគុណ",
      "questions": [
        {"number": 1, "question": "សំណួរ...", "choices": ["ក. ...", "ខ. ...", "គ. ...", "ឃ. ..."], "answer": "ក"}
      ]
    },
    {
      "section_title": "ផ្នែកទី២៖ សំណួរខ្លី",
      "questions": [
        {"number": 1, "question": "សំណួរ...", "answer": "ចម្លើយគំរូ"}
      ]
    }
  ]
}
"""

CURRICULUM_SCHEMA_HINT = """
{
  "subject": "មុខវិជ្ជា",
  "grade": "ថ្នាក់ទី",
  "school_year": "ឆ្នាំសិក្សា",
  "rows": [
    {
      "month": "ខែ (បង្ហាញតែនៅជួរដំបូងនៃខែនីមួយៗ)",
      "week_hours": "សប្តាហ៍ ន.ចំនួនម៉ោង (ឧ. ទី១ (១ម៉))",
      "lesson_content": "ខ្លឹមសារមេរៀន លម្អិត",
      "learning_outcome": "លទ្ធផលការសិក្សា",
      "page_rk": "ទំព័រ រ.ក",
      "page_rg": "ទំព័រ រ.គ"
    }
  ]
}
"""

SCHEMAS = {
    "lesson_plan": LESSON_PLAN_SCHEMA_HINT,
    "slide": SLIDE_SCHEMA_HINT,
    "test": TEST_SCHEMA_HINT,
    "curriculum": CURRICULUM_SCHEMA_HINT,
}

TOOL_INSTRUCTIONS = {
    "lesson_plan": (
        "អ្នកគឺជាគ្រូបង្រៀនជំនាញខ្ពស់នៅកម្ពុជា។ សូមអានខ្លឹមសារមេរៀន (ពីឯកសារ/រូបភាពដែលបានភ្ជាប់ "
        "និង/ឬពីអត្ថបទដែលគ្រូបានសរសេរផ្ទាល់ខាងក្រោម) រួចបង្កើត 'កិច្ចតែងការបង្រៀន' ពេញលេញជាភាសាខ្មែរ "
        "ដោយធ្វើតាមទម្រង់ស្តង់ដារក្រសួងអប់រំកម្ពុជា (ដូចគំរូ)។ សូមប្រើវិធីសាស្ត្របង្រៀនដែលបានស្នើ "
        "ហើយសរសេរខ្លឹមសារមេរៀនប្រចាំថ្ងៃឲ្យលម្អិត គ្រប់គ្រាន់សម្រាប់ម៉ោងបង្រៀនដែលបានផ្តល់។ "
        "ប្រសិនបើគ្រូបានសរសេរខ្លឹមសារមេរៀនផ្ទាល់ សូមប្រើអត្ថបទនោះជាមូលដ្ឋានចម្បង ហើយរៀបចំរចនាសម្ព័ន្ធ "
        "ឲ្យត្រូវតាមទម្រង់កិច្ចតែងការវិញ មិនមែនចម្លងតែម្តងទេ។"
    ),
    "slide": (
        "អ្នកគឺជាអ្នកជំនាញរៀបចំបទបង្ហាញអប់រំដូចម៉ូដែលរបស់ក្រសួងអប់រំ យុវជន និងកីឡាកម្ពុជា។ "
        "ដោយផ្អែកលើខ្លឹមសារកិច្ចតែងការ/មេរៀនដែលបានផ្តល់ សូមបំបែកជាស្លាយ (slides) ជាភាសាខ្មែរ ចន្លោះពី ៦ ទៅ ១២ ស្លាយ។ "
        "ជ្រើសរើស 'type' ដ៏សមស្របបំផុតសម្រាប់ខ្លឹមសារនីមួយៗ (cover សម្រាប់ស្លាយបើក, bullets សម្រាប់ចំណុចសំខាន់ៗ, "
        "two_column សម្រាប់ការពន្យល់វែង, cards សម្រាប់ជំហាន/ដំណាក់កាលច្រើនក្នុងជួរដេក, timeline សម្រាប់លំដាប់ព្រឹត្តិការណ៍, "
        "table សម្រាប់ទិន្នន័យតារាង, compare សម្រាប់ប្រៀបធៀបពីរចំណុច, section សម្រាប់ស្លាយផ្តាច់វគ្គ/សំណួរដឹកនាំគំនិត, "
        "closing សម្រាប់ស្លាយបញ្ចប់/ពិនិត្យឡើងវិញ)។ ខ្លីៗច្បាស់លាស់ សមស្របសម្រាប់បង្ហាញលើអេក្រង់ថ្នាក់រៀន "
        "(មិនមែនអត្ថបទវែងសម្រាប់អាន)។"
    ),
    "test": (
        "អ្នកគឺជាអ្នកជំនាញរៀបចំតេស្តអប់រំ។ ដោយផ្អែកលើខ្លឹមសារមេរៀនដែលបានផ្តល់ "
        "សូមបង្កើតតេស្តស្តង់ដារជាភាសាខ្មែរ មានទាំងសំណួរជម្រើសពហុគុណ និងសំណួរខ្លី ព្រមទាំងចម្លើយគំរូ។"
    ),
    "curriculum": (
        "អ្នកគឺជាអ្នកជំនាញកម្មវិធីសិក្សា។ ដោយផ្អែកលើខ្លឹមសារសៀវភៅសិក្សាដែលបានផ្តល់ "
        "សូមបំបែងចែកកម្មវិធីសិក្សាតាមខែ/សប្តាហ៍ ជាភាសាខ្មែរ ដូចទម្រង់តារាងបំបែងកម្មវិធីសិក្សាស្តង់ដារ។"
    ),
}


def generate_content(tool_type, hours, lesson_date, method, filepaths, extra_notes="", lesson_text=""):
    """
    tool_type: 'lesson_plan' | 'slide' | 'test' | 'curriculum'
    filepaths: list of uploaded source files (photo of textbook page, existing lesson plan, etc.)
    lesson_text: optional lesson content typed directly by the teacher, used instead of
                 (or in addition to) uploaded files.
    Returns: dict (parsed JSON matching the schema for tool_type)
    """
    if tool_type not in SCHEMAS:
        raise ValueError(f"មិនស្គាល់ tool_type: {tool_type}")
    if not filepaths and not (lesson_text and lesson_text.strip()):
        raise ValueError("ត្រូវការឯកសារ/រូបភាព ឬអត្ថបទមេរៀនយ៉ាងហោចណាស់មួយ")

    method_label = METHOD_LABELS.get(method, method or "")
    lesson_text_block = (
        f"\nខ្លឹមសារមេរៀនដែលគ្រូបានសរសេរផ្ទាល់៖\n\"\"\"\n{lesson_text.strip()}\n\"\"\"\n"
        if lesson_text and lesson_text.strip()
        else ""
    )
    prompt_text = f"""{TOOL_INSTRUCTIONS[tool_type]}

ព័ត៌មានបន្ថែម៖
- ចំនួនម៉ោងបង្រៀន៖ {hours}
- កាលបរិច្ឆេទបង្រៀន៖ {lesson_date}
- វិធីសាស្ត្របង្រៀន៖ {method_label}
- កំណត់សម្គាល់បន្ថែម៖ {extra_notes or "គ្មាន"}
{lesson_text_block}
សូមឆ្លើយតបជា JSON សុទ្ធសាធតែមួយប៉ុណ្ណោះ (គ្មានអត្ថបទពន្យល់ គ្មាន ```json fences) ដោយអនុវត្តតាមទម្រង់ (schema) ខាងក្រោមយ៉ាងតឹងរ៉ឹង៖

{SCHEMAS[tool_type]}
"""

    provider = _provider()
    if provider == "gemini":
        return _generate_with_gemini(prompt_text, filepaths)
    return _generate_with_anthropic(prompt_text, filepaths)


def _generate_with_anthropic(prompt_text, filepaths):
    client = _anthropic_client()
    content_blocks = [_file_to_content_block(fp) for fp in filepaths]
    content_blocks.append({"type": "text", "text": prompt_text})

    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": content_blocks}],
    )
    text_out = "".join(block.text for block in message.content if block.type == "text")
    return _extract_json(text_out)


def _generate_with_gemini(prompt_text, filepaths):
    from google.genai import types

    client = _gemini_client()
    parts = [_file_to_gemini_part(fp) for fp in filepaths]
    parts.append(types.Part.from_text(text=prompt_text))

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[types.Content(role="user", parts=parts)],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            max_output_tokens=8000,
        ),
    )
    return _extract_json(response.text)


CHAT_SYSTEM_PROMPT = (
    "អ្នកគឺជា AI ជំនួយការគាំទ្រសម្រាប់កម្មវិធី 'ជំនួយការគ្រូ AI' — ឧបករណ៍ជួយគ្រូបង្រៀនកម្ពុជាបង្កើតកិច្ចតែងការបង្រៀន, "
    "ស្លាយ, តេស្ត, និងកម្មវិធីសិក្សាដោយប្រើ AI។ អ្នកកំពុងឆ្លើយសំណួររបស់គ្រូបង្រៀនម្នាក់ក្នុងប្រអប់ជជែក (chat) ។ "
    "ឆ្លើយជាភាសាខ្មែរ ខ្លីៗ ច្បាស់លាស់ ស្និទ្ធស្នាល និងមានប្រយោជន៍។ បើសំណួរទាក់ទងនឹងរបៀបប្រើប្រាស់កម្មវិធីនេះ សូមណែនាំតាមចំណេះដឹងទូទៅ។ "
    "បើសំណួរជាបញ្ហាបច្ចេកទេស ស្មុគស្មាញ ឬទាមទារសិទ្ធិអ្នកគ្រប់គ្រង (ឧ. ការទូទាត់ប្រាក់, បញ្ហាគណនី, បណ្តឹង) សូមប្រាប់ថាអ្នកនឹងជូនដំណឹងទៅ admin ជូនអ្នកប្រើ។ "
    "កុំប្រឌិតព័ត៌មានមិនប្រាកដ។"
)


def chat_reply(history):
    """
    Generate a short conversational reply for the support chat.
    history: list of {"role": "user"|"assistant", "content": str}, oldest first.
    Returns: plain text reply (str).
    """
    provider = _provider()
    if provider == "gemini":
        return _chat_reply_gemini(history)
    return _chat_reply_anthropic(history)


def _chat_reply_anthropic(history):
    client = _anthropic_client()
    messages = [{"role": h["role"], "content": h["content"]} for h in history]
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1000,
        system=CHAT_SYSTEM_PROMPT,
        messages=messages,
    )
    return "".join(block.text for block in message.content if block.type == "text").strip()


def _chat_reply_gemini(history):
    from google.genai import types

    client = _gemini_client()
    contents = [
        types.Content(
            role=("model" if h["role"] == "assistant" else "user"),
            parts=[types.Part.from_text(text=h["content"])],
        )
        for h in history
    ]
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=CHAT_SYSTEM_PROMPT,
            max_output_tokens=1000,
        ),
    )
    return (response.text or "").strip()
