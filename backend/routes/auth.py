import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token

from extensions import db, bcrypt
from models import User

auth_bp = Blueprint("auth", __name__)


def _allowed(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


@auth_bp.post("/register")
def register():
    # multipart/form-data (to allow optional photo upload) or JSON
    if request.content_type and "multipart/form-data" in request.content_type:
        data = request.form
        photo = request.files.get("photo")
    else:
        data = request.get_json(force=True) or {}
        photo = None

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()
    gender = data.get("gender")
    dob = data.get("date_of_birth")
    school_name = data.get("school_name")
    subject = data.get("subject")

    if not username or not password or not full_name:
        return jsonify({"error": "សូមបំពេញ ឈ្មោះអ្នកប្រើ ពាក្យសម្ងាត់ និងឈ្មោះ"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "ឈ្មោះអ្នកប្រើនេះមានរួចហើយ"}), 409

    photo_path = None
    if photo and photo.filename and _allowed(photo.filename):
        fname = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
        photo.save(os.path.join(current_app.config["UPLOAD_FOLDER"], fname))
        photo_path = fname

    user = User(
        username=username,
        full_name=full_name,
        gender=gender,
        date_of_birth=datetime.strptime(dob, "%Y-%m-%d").date() if dob else None,
        school_name=school_name,
        subject=subject,
        photo_path=photo_path,
        role="user",
    )
    user.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(force=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "ឈ្មោះអ្នកប្រើ ឬពាក្យសម្ងាត់មិនត្រឹមត្រូវ"}), 401

    if not user.is_active:
        return jsonify({"error": "គណនីនេះត្រូវបានផ្អាក សូមទាក់ទងអ្នកគ្រប់គ្រង"}), 403

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"token": token, "user": user.to_dict()}), 200
