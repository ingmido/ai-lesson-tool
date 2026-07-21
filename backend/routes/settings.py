from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

from extensions import db
from models import SiteSettings
from services.storage import upload_avatar

settings_bp = Blueprint("settings", __name__)

DEFAULT_ABOUT = {
    "mission_text": (
        "ជំនួយការគ្រូ AI ត្រូវបានបង្កើតឡើងដើម្បីជួយសម្រួលបន្ទុកការងាររៀបចំឯកសារបង្រៀនរបស់គ្រូបង្រៀនកម្ពុជា — "
        "ចាប់ពីកិច្ចតែងការបង្រៀន ស្លាយបង្ហាញ តេស្តវាយតម្លៃ រហូតដល់ការបំបែងចែកកម្មវិធីសិក្សា — "
        "ដោយប្រើប្រាស់បច្ចេកវិទ្យា AI ដើម្បីសន្សំពេលវេលា ឲ្យគ្រូបានផ្តោតលើការបង្រៀនសិស្សឲ្យបានច្រើនជាងមុន។"
    ),
    "contact_name": "អ៊ីង មីដូ",
    "contact_school": "វិទ្យាល័យ ហ៊ុន សែន ចំណាលើ",
    "contact_specialty": "ព័ត៌មានវិទ្យា",
    "contact_facebook": "Ing Rado",
    "contact_telegram": "@rado2023",
    "contact_photo_url": None,
}


def _get_or_create_settings():
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings(**DEFAULT_ABOUT)
        db.session.add(settings)
        db.session.commit()
    return settings


@settings_bp.get("/about")
@jwt_required()
def get_about():
    settings = _get_or_create_settings()
    return jsonify(settings.to_dict())


@settings_bp.put("/admin/about")
@jwt_required()
def update_about():
    from flask_jwt_extended import get_jwt

    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "តម្រូវការសិទ្ធិអ្នកគ្រប់គ្រង (Admin) ប៉ុណ្ណោះ"}), 403

    settings = _get_or_create_settings()
    data = request.get_json(force=True) or {}
    for field in ("mission_text", "contact_name", "contact_school", "contact_specialty", "contact_facebook", "contact_telegram"):
        if field in data:
            setattr(settings, field, data[field])
    db.session.commit()
    return jsonify(settings.to_dict())


@settings_bp.post("/admin/about/photo")
@jwt_required()
def upload_about_photo():
    from flask_jwt_extended import get_jwt

    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "តម្រូវការសិទ្ធិអ្នកគ្រប់គ្រង (Admin) ប៉ុណ្ណោះ"}), 403

    photo = request.files.get("photo")
    if not photo or not photo.filename:
        return jsonify({"error": "សូមជ្រើសរើសរូបថត"}), 400

    settings = _get_or_create_settings()
    settings.contact_photo_url = upload_avatar(photo, current_app.config["UPLOAD_FOLDER"])
    db.session.commit()
    return jsonify(settings.to_dict())
