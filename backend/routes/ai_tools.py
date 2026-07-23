import os
import json
import uuid
from datetime import datetime, time
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from extensions import db
from models import Generation
from services.claude_service import generate_content

ai_bp = Blueprint("ai_tools", __name__)

VALID_TOOLS = {"lesson_plan", "slide", "test", "curriculum"}


def _allowed(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def _today_generation_count(user_id):
    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    return Generation.query.filter(
        Generation.user_id == user_id,
        Generation.created_at >= today_start,
    ).count()


@ai_bp.get("/usage-today")
@jwt_required()
def usage_today():
    user_id = int(get_jwt_identity())
    limit = current_app.config["MAX_AI_GENERATIONS_PER_DAY"]
    used = _today_generation_count(user_id)
    return jsonify({"used": used, "limit": limit, "unlimited": limit <= 0})


@ai_bp.post("/<tool_type>/generate")
@jwt_required()
def generate(tool_type):
    if tool_type not in VALID_TOOLS:
        return jsonify({"error": "tool_type មិនត្រឹមត្រូវ"}), 400

    user_id = int(get_jwt_identity())
    is_admin = get_jwt().get("role") == "admin"

    limit = current_app.config["MAX_AI_GENERATIONS_PER_DAY"]
    if not is_admin and limit > 0:
        used = _today_generation_count(user_id)
        if used >= limit:
            return jsonify({
                "error": f"អ្នកបានប្រើប្រាស់ AI លើសកំណត់ថ្ងៃនេះហើយ ({limit} ដង/ថ្ងៃ)។ សូមព្យាយាមម្តងទៀតថ្ងៃស្អែក ឬទាក់ទង admin។"
            }), 429

    hours = request.form.get("hours", "")
    lesson_date = request.form.get("lesson_date", "")
    method = request.form.get("method", "")
    extra_notes = request.form.get("extra_notes", "")
    title = request.form.get("title", "")
    style = request.form.get("style", "teal_light")
    lesson_text = request.form.get("lesson_text", "")

    saved_paths = []
    saved_names = []
    for f in request.files.getlist("files"):
        if f and f.filename and _allowed(f.filename):
            fname = f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
            path = os.path.join(current_app.config["UPLOAD_FOLDER"], fname)
            f.save(path)
            saved_paths.append(path)
            saved_names.append(fname)

    if not saved_paths and not lesson_text.strip():
        return jsonify({"error": "សូមភ្ជាប់ឯកសារ/រូបថត ឬសរសេរខ្លឹមសារមេរៀនផ្ទាល់យ៉ាងហោចណាស់មួយយ៉ាង"}), 400

    try:
        result_json = generate_content(
            tool_type=tool_type,
            hours=hours,
            lesson_date=lesson_date,
            method=method,
            filepaths=saved_paths,
            extra_notes=extra_notes,
            lesson_text=lesson_text,
        )
    except Exception as e:
        current_app.logger.exception("AI generation failed")
        return jsonify({"error": f"បរាជ័យក្នុងការបង្កើតខ្លឹមសារ៖ {str(e)}"}), 502

    gen = Generation(
        user_id=user_id,
        tool_type=tool_type,
        style=style if tool_type == "slide" else None,
        title=title or result_json.get("title") or result_json.get("subject") or "គ្មានចំណងជើង",
        teaching_method=method,
        lesson_date=datetime.strptime(lesson_date, "%Y-%m-%d").date() if lesson_date else None,
        lesson_hours=float(hours) if hours else None,
        content_json=json.dumps(result_json, ensure_ascii=False),
        source_filename=",".join(saved_names),
    )
    db.session.add(gen)
    db.session.commit()

    return jsonify({"generation": gen.to_dict(), "content": result_json}), 201


@ai_bp.get("/<tool_type>/history")
@jwt_required()
def history(tool_type):
    if tool_type not in VALID_TOOLS:
        return jsonify({"error": "tool_type មិនត្រឹមត្រូវ"}), 400
    user_id = int(get_jwt_identity())
    items = (
        Generation.query.filter_by(user_id=user_id, tool_type=tool_type)
        .order_by(Generation.created_at.desc())
        .all()
    )
    return jsonify([g.to_dict() for g in items])


@ai_bp.get("/generation/<int:gen_id>")
@jwt_required()
def get_generation(gen_id):
    user_id = int(get_jwt_identity())
    gen = Generation.query.get_or_404(gen_id)
    if gen.user_id != user_id:
        return jsonify({"error": "គ្មានសិទ្ធិចូលមើល"}), 403
    data = gen.to_dict()
    data["content"] = json.loads(gen.content_json) if gen.content_json else {}
    return jsonify(data)


@ai_bp.put("/generation/<int:gen_id>")
@jwt_required()
def update_generation(gen_id):
    """ធ្វើបច្ចុប្បន្នភាពខ្លឹមសារ បន្ទាប់ពីអ្នកប្រើកែសម្រួល manual មុននឹង export"""
    user_id = int(get_jwt_identity())
    gen = Generation.query.get_or_404(gen_id)
    if gen.user_id != user_id:
        return jsonify({"error": "គ្មានសិទ្ធិកែប្រែ"}), 403

    payload = request.get_json(force=True) or {}
    if "content" in payload:
        gen.content_json = json.dumps(payload["content"], ensure_ascii=False)
    if "title" in payload:
        gen.title = payload["title"]
    if "style" in payload:
        gen.style = payload["style"]
    db.session.commit()
    return jsonify(gen.to_dict())


@ai_bp.delete("/generation/<int:gen_id>")
@jwt_required()
def delete_generation(gen_id):
    user_id = int(get_jwt_identity())
    gen = Generation.query.get_or_404(gen_id)
    if gen.user_id != user_id:
        return jsonify({"error": "គ្មានសិទ្ធិលុប"}), 403
    db.session.delete(gen)
    db.session.commit()
    return jsonify({"message": "លុបជោគជ័យ"})
