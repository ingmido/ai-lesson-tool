from functools import wraps
from datetime import datetime, time, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import func

from extensions import db, bcrypt
from models import User, Generation, ChatMessage

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


@admin_bp.get("/stats")
@admin_required
def get_stats():
    now = datetime.utcnow()
    today_start = datetime.combine(now.date(), time.min)
    week_ago = now - timedelta(days=7)

    total_users = User.query.filter(User.role == "user").count()
    new_users_7d = User.query.filter(User.role == "user", User.created_at >= week_ago).count()
    new_users_today = User.query.filter(User.role == "user", User.created_at >= today_start).count()

    total_generations = Generation.query.count()
    generations_today = Generation.query.filter(Generation.created_at >= today_start).count()
    generations_7d = Generation.query.filter(Generation.created_at >= week_ago).count()

    by_tool = (
        db.session.query(Generation.tool_type, func.count(Generation.id))
        .group_by(Generation.tool_type)
        .all()
    )

    total_chat_messages = ChatMessage.query.count()
    ai_replies_today = ChatMessage.query.filter(
        ChatMessage.sender_role == "ai", ChatMessage.created_at >= today_start
    ).count()

    # Users closest to hitting today's generation cap, useful for spotting heavy usage
    top_users_today = (
        db.session.query(Generation.user_id, func.count(Generation.id).label("cnt"))
        .filter(Generation.created_at >= today_start)
        .group_by(Generation.user_id)
        .order_by(func.count(Generation.id).desc())
        .limit(5)
        .all()
    )
    top_users = []
    for uid, cnt in top_users_today:
        u = User.query.get(uid)
        if u:
            top_users.append({"user_id": uid, "full_name": u.full_name, "count": cnt})

    return jsonify({
        "total_users": total_users,
        "new_users_today": new_users_today,
        "new_users_7d": new_users_7d,
        "total_generations": total_generations,
        "generations_today": generations_today,
        "generations_7d": generations_7d,
        "by_tool": {t: c for t, c in by_tool},
        "total_chat_messages": total_chat_messages,
        "ai_replies_today": ai_replies_today,
        "top_users_today": top_users,
    })
