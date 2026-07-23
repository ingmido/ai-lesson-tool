import os
import json
import uuid
import subprocess
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import Generation, User
from services.docx_export import export_to_docx, build_google_form_script
from services.pptx_export import build_pptx

export_bp = Blueprint("export", __name__)


@export_bp.get("/<int:gen_id>/pptx")
@jwt_required()
def export_pptx(gen_id):
    user_id = int(get_jwt_identity())
    gen = Generation.query.get_or_404(gen_id)
    if gen.user_id != user_id:
        return jsonify({"error": "គ្មានសិទ្ធិចូលមើល"}), 403
    if gen.tool_type != "slide":
        return jsonify({"error": "PowerPoint export ប្រើបានតែសម្រាប់ឧបករណ៍ Slide ប៉ុណ្ណោះ"}), 400

    data = json.loads(gen.content_json) if gen.content_json else {}
    fname = f"slide_{gen.id}_{uuid.uuid4().hex[:6]}.pptx"
    out_path = os.path.join(current_app.config["EXPORT_FOLDER"], fname)

    build_pptx(data, gen.style or "teal_light", out_path)

    return send_file(out_path, as_attachment=True, download_name=fname)


@export_bp.get("/<int:gen_id>/docx")
@jwt_required()
def export_docx(gen_id):
    user_id = int(get_jwt_identity())
    gen = Generation.query.get_or_404(gen_id)
    if gen.user_id != user_id:
        return jsonify({"error": "គ្មានសិទ្ធិចូលមើល"}), 403

    user = User.query.get(user_id)
    data = json.loads(gen.content_json) if gen.content_json else {}

    fname = f"{gen.tool_type}_{gen.id}_{uuid.uuid4().hex[:6]}.docx"
    out_path = os.path.join(current_app.config["EXPORT_FOLDER"], fname)

    kwargs = {}
    if gen.tool_type == "lesson_plan":
        kwargs = {"teacher_name": user.full_name if user else "", "school_name": user.school_name if user else ""}

    export_to_docx(gen.tool_type, data, out_path, **kwargs)

    return send_file(out_path, as_attachment=True, download_name=fname)


@export_bp.get("/<int:gen_id>/pdf")
@jwt_required()
def export_pdf(gen_id):
    """Converts the generated .docx (or .pptx for slides) to PDF via LibreOffice (soffice) headless."""
    user_id = int(get_jwt_identity())
    gen = Generation.query.get_or_404(gen_id)
    if gen.user_id != user_id:
        return jsonify({"error": "គ្មានសិទ្ធិចូលមើល"}), 403

    user = User.query.get(user_id)
    data = json.loads(gen.content_json) if gen.content_json else {}

    if gen.tool_type == "slide":
        fname = f"slide_{gen.id}_{uuid.uuid4().hex[:6]}.pptx"
        out_path = os.path.join(current_app.config["EXPORT_FOLDER"], fname)
        build_pptx(data, gen.style or "teal_light", out_path)
    else:
        fname = f"{gen.tool_type}_{gen.id}_{uuid.uuid4().hex[:6]}.docx"
        out_path = os.path.join(current_app.config["EXPORT_FOLDER"], fname)
        kwargs = {}
        if gen.tool_type == "lesson_plan":
            kwargs = {"teacher_name": user.full_name if user else "", "school_name": user.school_name if user else ""}
        export_to_docx(gen.tool_type, data, out_path, **kwargs)

    try:
        subprocess.run(
            [
                "soffice", "--headless", "--convert-to", "pdf",
                "--outdir", current_app.config["EXPORT_FOLDER"], out_path,
            ],
            check=True, timeout=60,
        )
    except Exception as e:
        return jsonify({
            "error": "ការបំប្លែងទៅ PDF បរាជ័យ (តម្រូវឲ្យដំឡើង LibreOffice នៅលើម៉ាស៊ីនមេ)។ "
                     "អ្នកអាចទាញយកជា Word រួចបោះពុម្ព/Save as PDF ដោយផ្ទាល់។",
            "detail": str(e),
        }), 500

    pdf_path = out_path.rsplit(".", 1)[0] + ".pdf"
    return send_file(pdf_path, as_attachment=True, download_name=os.path.basename(pdf_path))


@export_bp.get("/<int:gen_id>/google-form-script")
@jwt_required()
def export_google_form_script(gen_id):
    """
    Returns a Google Apps Script (.gs) file. The teacher pastes this into
    script.google.com and runs it to create a real Google Form quiz under
    their own account — no Google API credentials needed on our backend.
    """
    user_id = int(get_jwt_identity())
    gen = Generation.query.get_or_404(gen_id)
    if gen.user_id != user_id:
        return jsonify({"error": "គ្មានសិទ្ធិចូលមើល"}), 403
    if gen.tool_type != "test":
        return jsonify({"error": "អាច Export ទៅ Google Form បានតែពី tool តេស្តប៉ុណ្ណោះ"}), 400

    data = json.loads(gen.content_json) if gen.content_json else {}
    script_text = build_google_form_script(data)

    fname = f"google_form_script_{gen.id}.gs"
    out_path = os.path.join(current_app.config["EXPORT_FOLDER"], fname)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(script_text)

    return send_file(out_path, as_attachment=True, download_name=fname, mimetype="text/plain")
