import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db, bcrypt
from models import User

profile_bp = Blueprint("profile", __name__)


def _allowed(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def _current_user():
    uid = get_jwt_identity()
    return User.query.get(int(uid))


@profile_bp.get("/me")
@jwt_required()
def get_me():
    user = _current_user()
    if not user:
        return jsonify({"error": "រកមិនឃើញអ្នកប្រើ"}), 404
    return jsonify(user.to_dict())


@profile_bp.put("/me")
@jwt_required()
def update_me():
    user = _current_user()
    if not user:
        return jsonify({"error": "រកមិនឃើញអ្នកប្រើ"}), 404

    if request.content_type and "multipart/form-data" in request.content_type:
        data = request.form
        photo = request.files.get("photo")
    else:
        data = request.get_json(force=True) or {}
        photo = None

    if data.get("full_name"):
        user.full_name = data.get("full_name")
    if data.get("gender"):
        user.gender = data.get("gender")
    if data.get("date_of_birth"):
        user.date_of_birth = datetime.strptime(data.get("date_of_birth"), "%Y-%m-%d").date()
    if data.get("school_name"):
        user.school_name = data.get("school_name")
    if data.get("subject"):
        user.subject = data.get("subject")
    if data.get("password"):
        user.password_hash = bcrypt.generate_password_hash(data.get("password")).decode("utf-8")

    if photo and photo.filename and _allowed(photo.filename):
        fname = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
        photo.save(os.path.join(current_app.config["UPLOAD_FOLDER"], fname))
        user.photo_path = fname

    db.session.commit()
    return jsonify(user.to_dict())
