# AI ជំនួយការគ្រូ — AI Teaching Toolkit

កម្មវិធីវេប Flask (backend) + Vue 3 / Tailwind (frontend) សម្រាប់គ្រូបង្រៀន៖
ចុះឈ្មោះ/ចូលគណនី, ប្រវត្តិរូប, dashboard admin, និងឧបករណ៍ AI ៤ មុខ៖

1. **កិច្ចតែងការបង្រៀន** — ថតរូប/បញ្ចូលឯកសារមេរៀន → AI បង្កើតកិច្ចតែងការពេញលេញ (ទម្រង់ដូចគំរូ PDF ទី១)
2. **បង្កើត Slide** — បំបែងខ្លឹមសារជាស្លាយបង្ហាញ **PowerPoint ពិតប្រាកដ** ជាមួយរចនាប័ទ្ម ៤ បែបឲ្យជ្រើសរើស
   (ទំនើប·ភ្លឺ, ទំនើប·ងងឹត, ផ្លូវការ MOEYS ខៀវ/មាស, រីករាយសម្រាប់កុមារ) ដែលយកតាមគំរូស្លាយបង្រៀនកម្ពុជាផ្ទាល់
3. **តេស្តស្តង់ដារ** — បង្កើតសំណួរ + ចម្លើយគំរូ
4. **បំបែងចែកកម្មវិធីសិក្សា** — តារាងបំបែងតាមខែ/សប្តាហ៍ (ទម្រង់ដូចគំរូ PDF ទី២)

Tool កិច្ចតែងការ/តេស្ត/កម្មវិធីសិក្សា អាចទាញយកជា **Word (.docx)** ឬ **PDF**។
Tool Slide អាចទាញយកជា **PowerPoint (.pptx)**, Word (គ្រោងអត្ថបទ), ឬ PDF។

---

## រចនាសម្ព័ន្ធគម្រោង

```
ai-lesson-tool/
├── backend/          Flask API (Python)
│   ├── app.py
│   ├── models.py     User, Generation
│   ├── routes/        auth, profile, admin, ai_tools, export
│   └── services/       claude_service.py (AI), docx_export.py (Word)
└── frontend/          Vue 3 + Vite + Tailwind
    └── src/views/      Login, Register, Dashboard, Profile, Admin,
                          LessonPlanTool, SlideTool, TestTool, CurriculumTool
```

---

## ការដំឡើង (Windows + Laragon)

### ១. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

copy .env.example .env
# បើកឯកសារ .env រួចជ្រើសរើស AI_PROVIDER (anthropic ឬ gemini) ហើយដាក់ API key ដែលត្រូវគ្នា
#   - Claude API key: https://console.anthropic.com/
#   - Gemini API key: https://aistudio.google.com/apikey
# ប្រសិនបើអ្នកមានតែ Gemini key ប៉ុណ្ណោះ គ្រាន់តែដាក់ AI_PROVIDER=gemini និង GEMINI_API_KEY=...
# គឺគ្រប់គ្រាន់ហើយ មិនចាំបាច់មាន ANTHROPIC_API_KEY ទេ

python app.py
```
Backend នឹងរត់នៅ `http://localhost:5000`។ Admin លំនាំដើម៖ `admin` / `admin1234`.

### ២. Frontend

```bash
cd frontend
npm install
npm run dev
```
Frontend នឹងរត់នៅ `http://localhost:5173` ហើយហៅ backend ដោយស្វ័យប្រវត្តិ (proxy កំណត់ក្នុង `vite.config.js`)។

### ៣. ការនាំចេញជា PDF (ស្រេចចិត្ត)

ការចុច "⬇ PDF" ត្រូវការ **LibreOffice** (`soffice`) ដំឡើងនៅលើម៉ាស៊ីនដែលរត់ backend។
- Windows: ទាញយក LibreOffice ពី https://www.libreoffice.org រួចដំឡើងធម្មតា។
- បើមិនចង់ដំឡើង LibreOffice ទេ អ្នកអាចទាញយកជា Word រួច "Print → Save as PDF" ដោយផ្ទាល់ក្នុង Word។

### ៤. ពុម្ពអក្សរខ្មែរសម្រាប់ Word

ឯកសារ .docx ដែល AI បង្កើត កំណត់ពុម្ពអក្សរ **Khmer OS Battambang**។ សូមប្រាកដថាមានពុម្ពនេះ
(ឬពុម្ពខ្មែរផ្សេងទៀត) ដំឡើងនៅលើកុំព្យូទ័រដែលបើកឯកសារ Word។

---

## ដាក់ដំណើរការជាសាធារណៈ (Deploy ដើម្បីឲ្យអ្នកដទៃប្រើបាន)

GitHub ខ្លួនឯង **មិនអាចរត់** Flask backend ឬបម្រើ website ផ្ទាល់បានទេ — វាគ្រាន់តែផ្ទុកកូដ។ ដើម្បីឲ្យអ្នកដទៃចូលប្រើវេបសាយបាន ត្រូវ **deploy** ទៅ hosting ។ ខាងក្រោមជាវិធីឥតគិតថ្លៃ (ឬថោក) ដែលងាយបំផុត៖ **Render** សម្រាប់ backend + **Netlify** សម្រាប់ frontend។

### ជំហានទី១៖ Deploy Backend (Render.com)

1. ចូល https://render.com → Sign up ដោយ GitHub account ដដែល
2. ចុច **New → Web Service** → ជ្រើសរើស repo `ai-lesson-tool`
3. កំណត់៖
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120` (Render រកឃើញពី `Procfile` ស្វ័យប្រវត្តិផងដែរ)
4. ក្នុងផ្នែក **Environment Variables** (នេះជាកន្លែងដាក់ API key — មិនមែនក្នុង Git ទេ) ដាក់៖
   - `AI_PROVIDER` = `gemini` (ឬ `anthropic`)
   - `GEMINI_API_KEY` = key របស់អ្នក
   - `SECRET_KEY` = អក្សរចៃដន្យវែងៗ
   - `JWT_SECRET_KEY` = អក្សរចៃដន្យវែងៗមួយទៀត
5. ចុច **Create Web Service** — Render នឹង build និង deploy ស្វ័យប្រវត្តិ។ URL ដែលបានគឺប្រហែល `https://ai-lesson-tool-xxxx.onrender.com`

**ចំណាំសំខាន់៖**
- Render free tier "spins down" បន្ទាប់ពី inactive ២០នាទី — request ដំបូងក្រោយពីនោះនឹងយឺត (~៣០វិនាទី)។
- **Disk មិនស្ថិតស្ថេរទេលើ free tier** — រាល់ពេល redeploy, ឯកសារ `app.db`, `uploads/`, `exports/` នឹងលុបចោល។ សម្រាប់ការប្រើប្រាស់ពិតប្រាកដ គួរបន្ថែម Render's **Persistent Disk** (មានតម្លៃបន្តិច) ឬប្តូរទៅ managed database (Postgres)។
- **PDF export នឹងមិនដំណើរការទេ** លើ Render free tier ព្រោះគ្មាន LibreOffice ដំឡើង — Word/PowerPoint export នៅតែដំណើរការធម្មតា។

### ជំហានទី២៖ Deploy Frontend (Netlify)

1. ចូល https://netlify.com → Sign up ដោយ GitHub
2. ចុច **Add new site → Import an existing project** → ជ្រើសរើស repo `ai-lesson-tool`
3. កំណត់៖
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
4. ក្នុងផ្នែក **Environment variables** ដាក់៖
   - `VITE_API_BASE_URL` = URL របស់ backend ពី Render (ឧ. `https://ai-lesson-tool-xxxx.onrender.com`) — **កុំដាក់ `/` ខាងចុង**
5. ចុច **Deploy** — Netlify ផ្តល់ URL ដូចជា `https://ai-lesson-tool.netlify.app` ដែលអ្នកអាចចែករំលែកបានភ្លាមៗ

ចំណាំ៖ `VITE_API_BASE_URL` ត្រូវកំណត់ **មុននឹង build** ព្រោះ Vite baked វាចូលក្នុងឯកសារ JS ស្ថិតស្ថេរតាំងពីពេល build។ បើផ្លាស់ប្តូរ backend URL ក្រោយ ត្រូវ redeploy frontend ម្តងទៀត។

### ការធ្វើតេស្តមុន deploy ជាសាធារណៈ

មុននឹងចែករំលែក URL ទៅអ្នកដទៃ សូមចូល URL frontend ដោយខ្លួនឯងសិន៖ ចុះឈ្មោះគណនីថ្មី, សាកល្បង generate កិច្ចតែងការ, ទាញយក Word — ដើម្បីប្រាកដថារបស់ទាំងអស់ភ្ជាប់គ្នាត្រឹមត្រូវ។

---

## របៀបប្រើប្រាស់

1. ចុះឈ្មោះគណនីគ្រូ (ឈ្មោះ, ភេទ, ថ្ងៃខែឆ្នាំកំណើត, សាលា, មុខវិជ្ជា, រូបថត)
2. ចូល Dashboard → ជ្រើសរើសឧបករណ៍ AI
3. ថត/ជ្រើសរូបភាព ឬ PDF នៃទំព័រសៀវភៅ/កិច្ចតែងការចាស់
4. បំពេញម៉ោង កាលបរិច្ឆេទ វិធីសាស្ត្របង្រៀន → ចុច "បង្កើតដោយ AI"
5. កែសម្រួលលទ្ធផលបានផ្ទាល់ (គ្រប់វាល text អាចកែបាន) → "រក្សាទុកការកែប្រែ"
6. ទាញយកជា Word ឬ PDF

Admin (គណនី `role=admin`) ចូល `/admin` ដើម្បីមើល/គ្រប់គ្រង/ផ្អាក/លុបគណនីអ្នកប្រើផ្សេងទៀត។

---

## ចំណុចសំខាន់ដែលគួរដឹង / ការពង្រីកបន្ថែម

- **AI generation** ប្រើ Claude ឬ Gemini (កំណត់ដោយ `AI_PROVIDER` ក្នុង `.env`) តាមរយៈ Vision API — វា "អាន" រូបភាព/PDF ដោយផ្ទាល់
  គ្មានតម្រូវការ OCR ដាច់ដោយឡែកទេ។ Prompt schema នីមួយៗនៅក្នុង
  `backend/services/claude_service.py` — អាចកែសម្រួល schema/instructions នៅទីនោះ។
  បើមិនកំណត់ `AI_PROVIDER` ច្បាស់លាស់ទេ ប្រព័ន្ធនឹងប្រើ Gemini ស្វ័យប្រវត្តិប្រសិនបើមាន `GEMINI_API_KEY`,
  បើគ្មានទេវានឹងប្រើ Anthropic។
- **Word export** ប្រើ `python-docx` ក្នុង `backend/services/docx_export.py`។ Layout កិច្ចតែងការ
  និងកម្មវិធីសិក្សាត្រូវបានសាងសង់ឲ្យស្រដៀងគំរូ PDF ដែលបានផ្តល់ — អាចលម្អិតបន្ថែម
  (font ណិត, logo ក្រសួង, ក្បាល/ជើងទំព័រ ។ល។) តាមតម្រូវការជាក់ស្តែង។
- **Slide tool** ផ្តល់លទ្ធផលជា JSON ជាមួយ "type" ក្នុងស្លាយនីមួយៗ (cover, bullets, two_column, cards,
  timeline, table, compare, section, closing)។ `backend/services/pptx_export.py` បំប្លែងទៅជា `.pptx`
  ពិតប្រាកដ តាមរចនាប័ទ្ម ៤ បែប (`STYLES` dict ក្នុងឯកសារនោះ) — អាចបន្ថែមរចនាប័ទ្មថ្មី ឬកែពណ៌បានតាមត្រូវការ។
  Word export របស់ស្លាយគឺជាគ្រោងអត្ថបទសម្រាប់អានលឿន មិនមែនជាទម្រង់ស្លាយចុងក្រោយទេ — សូមប្រើ `.pptx`។
- **Database**: SQLite លំនាំដើម (`backend/app.db`, បង្កើតស្វ័យប្រវត្តិ) — សមស្របសម្រាប់សាកល្បង/ប្រើម្នាក់ឯង។
  ប្រសិនបើដាក់ដំណើរការសម្រាប់សាលាច្រើននាក់ប្រើ គួរប្តូរទៅ PostgreសQL/MySQL។
- សូមកុំបញ្ចេញ `ANTHROPIC_API_KEY` របស់អ្នកជាសាធារណៈ ឬដាក់ក្នុង git repository។
