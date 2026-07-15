from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from extensions import db, bcrypt
from models import User

admin_bp = Blueprint("admin", __name__)


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "តម្រូវការសិទ្ធិអ្នកគ្រប់គ្រង (Admin) ប៉ុណ្ណោះ"}), 403
        return fn(*args, **kwargs)

    return wrapper


@admin_bp.get("/users")
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])


@admin_bp.put("/users/<int:user_id>")
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json(force=True) or {}

    if "role" in data and data["role"] in ("admin", "user"):
        user.role = data["role"]
    if "is_active" in data:
        user.is_active = bool(data["is_active"])
    if data.get("full_name"):
        user.full_name = data["full_name"]
    if data.get("password"):
        user.password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    db.session.commit()
    return jsonify(user.to_dict())


@admin_bp.delete("/users/<int:user_id>")
@admin_required
def delete_user(user_id):
    requester_id = int(get_jwt_identity())
    if requester_id == user_id:
        return jsonify({"error": "មិនអាចលុបគណនីខ្លួនឯងបានទេ"}), 400

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "លុបជោគជ័យ"})
