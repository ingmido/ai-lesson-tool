from functools import wraps
from datetime import datetime, time
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import func

from extensions import db
from models import ChatMessage, User
from services.claude_service import chat_reply

chat_bp = Blueprint("chat", __name__)


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "តម្រូវការសិទ្ធិអ្នកគ្រប់គ្រង (Admin) ប៉ុណ្ណោះ"}), 403
        return fn(*args, **kwargs)

    return wrapper


def _build_ai_history(user_id, limit=20):
    """Turn recent chat_messages for this user into Anthropic/Gemini-style role history."""
    recent = (
        ChatMessage.query.filter_by(user_id=user_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    recent.reverse()
    history = []
    for m in recent:
        role = "user" if m.sender_role == "user" else "assistant"
        # collapse consecutive same-role turns isn't required by either API, so just map directly
        history.append({"role": role, "content": m.content})
    return history


def _today_ai_reply_count(user_id):
    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    return ChatMessage.query.filter(
        ChatMessage.user_id == user_id,
        ChatMessage.sender_role == "ai",
        ChatMessage.created_at >= today_start,
    ).count()


AI_FAILURE_FALLBACK = (
    "🤖 សូមទោស! AI ជំនួយការមិនអាចឆ្លើយបានទេពេលនេះ (ប្រព័ន្ធកំពុងមមាញឹក ឬដល់ដែនកំណត់ប្រើប្រាស់ថ្ងៃនេះ)។ "
    "សូមរង់ចាំបន្តិច ឬ admin នឹងឆ្លើយវិញឆាប់ៗនេះ។"
)

AI_DAILY_LIMIT_MESSAGE = (
    "🤖 អ្នកបានឈាន់ដល់ចំនួនកំណត់នៃការឆ្លើយតបដោយ AI សម្រាប់ថ្ងៃនេះហើយ។ "
    "សូមទាក់ទង admin ដោយផ្ទាល់ ឬសរសេរសារបន្ថែម admin នឹងឆ្លើយវិញ។"
)


def _maybe_ai_reply(user_id):
    """If AI auto-reply is enabled for this teacher, generate and store one.
    On failure (quota exhausted, network error, etc.), store a short apology
    instead of leaving the teacher's message unanswered with no explanation."""
    user = User.query.get(user_id)
    if not user or not user.chat_ai_enabled:
        return None

    history = _build_ai_history(user_id)
    if not history or history[-1]["role"] != "user":
        return None

    daily_limit = current_app.config.get("MAX_AI_CHAT_REPLIES_PER_DAY", 0)
    if daily_limit > 0 and _today_ai_reply_count(user_id) >= daily_limit:
        # Only send the "limit reached" notice once per day, not on every message.
        already_notified = ChatMessage.query.filter(
            ChatMessage.user_id == user_id,
            ChatMessage.sender_role == "ai",
            ChatMessage.content == AI_DAILY_LIMIT_MESSAGE,
            ChatMessage.created_at >= datetime.combine(datetime.utcnow().date(), time.min),
        ).first()
        if already_notified:
            return None
        ai_msg = ChatMessage(user_id=user_id, sender_role="ai", sender_id=None, content=AI_DAILY_LIMIT_MESSAGE)
        db.session.add(ai_msg)
        db.session.commit()
        return ai_msg

    try:
        reply_text = chat_reply(history)
        if not reply_text:
            reply_text = AI_FAILURE_FALLBACK
    except Exception:
        current_app.logger.exception("AI chat reply failed")
        reply_text = AI_FAILURE_FALLBACK

    ai_msg = ChatMessage(user_id=user_id, sender_role="ai", sender_id=None, content=reply_text)
    db.session.add(ai_msg)
    db.session.commit()
    return ai_msg


# ---------- Teacher (regular user) endpoints: my own conversation with admin ----------

@chat_bp.get("/messages")
@jwt_required()
def get_my_messages():
    user_id = int(get_jwt_identity())
    messages = (
        ChatMessage.query.filter_by(user_id=user_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    # Mark admin/AI messages as read since the teacher is viewing them now
    unread = [m for m in messages if m.sender_role in ("admin", "ai") and not m.is_read]
    for m in unread:
        m.is_read = True
    if unread:
        db.session.commit()

    return jsonify([m.to_dict() for m in messages])


@chat_bp.post("/messages")
@jwt_required()
def send_my_message():
    user_id = int(get_jwt_identity())
    data = request.get_json(force=True) or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "សូមសរសេរសារ"}), 400

    msg = ChatMessage(user_id=user_id, sender_role="user", sender_id=user_id, content=content)
    db.session.add(msg)
    db.session.commit()

    ai_msg = _maybe_ai_reply(user_id)

    return jsonify({"message": msg.to_dict(), "ai_reply": ai_msg.to_dict() if ai_msg else None}), 201


@chat_bp.get("/unread-count")
@jwt_required()
def my_unread_count():
    user_id = int(get_jwt_identity())
    count = ChatMessage.query.filter(
        ChatMessage.user_id == user_id,
        ChatMessage.sender_role.in_(["admin", "ai"]),
        ChatMessage.is_read.is_(False),
    ).count()
    return jsonify({"unread": count})


@chat_bp.get("/ai-setting")
@jwt_required()
def get_my_ai_setting():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify({"chat_ai_enabled": user.chat_ai_enabled})


@chat_bp.put("/ai-setting")
@jwt_required()
def set_my_ai_setting():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json(force=True) or {}
    if "chat_ai_enabled" in data:
        user.chat_ai_enabled = bool(data["chat_ai_enabled"])
        db.session.commit()
    return jsonify({"chat_ai_enabled": user.chat_ai_enabled})


# ---------- Admin endpoints: inbox across all teachers ----------

@chat_bp.get("/admin/conversations")
@admin_required
def list_conversations():
    # One row per user_id, with last message time + unread count (messages from the teacher, unread by admin)
    rows = (
        db.session.query(
            ChatMessage.user_id,
            func.max(ChatMessage.created_at).label("last_at"),
        )
        .group_by(ChatMessage.user_id)
        .order_by(func.max(ChatMessage.created_at).desc())
        .all()
    )

    result = []
    for user_id, last_at in rows:
        user = User.query.get(user_id)
        if not user:
            continue
        last_msg = (
            ChatMessage.query.filter_by(user_id=user_id)
            .order_by(ChatMessage.created_at.desc())
            .first()
        )
        unread = ChatMessage.query.filter_by(user_id=user_id, sender_role="user", is_read=False).count()
        result.append({
            "user_id": user_id,
            "full_name": user.full_name,
            "username": user.username,
            "school_name": user.school_name,
            "last_message": last_msg.content if last_msg else "",
            "last_at": last_at.isoformat() if last_at else None,
            "unread": unread,
            "chat_ai_enabled": user.chat_ai_enabled,
        })
    return jsonify(result)


@chat_bp.get("/admin/conversations/<int:user_id>")
@admin_required
def get_conversation(user_id):
    User.query.get_or_404(user_id)
    messages = (
        ChatMessage.query.filter_by(user_id=user_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    unread = [m for m in messages if m.sender_role == "user" and not m.is_read]
    for m in unread:
        m.is_read = True
    if unread:
        db.session.commit()

    return jsonify([m.to_dict() for m in messages])


@chat_bp.post("/admin/conversations/<int:user_id>/reply")
@admin_required
def reply_to_conversation(user_id):
    admin_id = int(get_jwt_identity())
    User.query.get_or_404(user_id)
    data = request.get_json(force=True) or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "សូមសរសេរសារ"}), 400

    msg = ChatMessage(user_id=user_id, sender_role="admin", sender_id=admin_id, content=content)
    db.session.add(msg)
    db.session.commit()
    return jsonify(msg.to_dict()), 201


@chat_bp.get("/admin/unread-total")
@admin_required
def admin_unread_total():
    count = ChatMessage.query.filter_by(sender_role="user", is_read=False).count()
    return jsonify({"unread": count})


@chat_bp.put("/admin/conversations/<int:user_id>/ai-toggle")
@admin_required
def toggle_ai_for_conversation(user_id):
    """Admin can turn AI auto-reply off (take over manually) or back on for a given teacher."""
    user = User.query.get_or_404(user_id)
    data = request.get_json(force=True) or {}
    if "chat_ai_enabled" in data:
        user.chat_ai_enabled = bool(data["chat_ai_enabled"])
        db.session.commit()
    return jsonify({"user_id": user.id, "chat_ai_enabled": user.chat_ai_enabled})
