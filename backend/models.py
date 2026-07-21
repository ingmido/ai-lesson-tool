from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # ព័ត៌មានផ្ទាល់ខ្លួន (Profile fields per spec)
    full_name = db.Column(db.String(150), nullable=False)
    gender = db.Column(db.String(20))  # ភេទ
    date_of_birth = db.Column(db.Date)  # ថ្ងៃខែឆ្នាំកំណើត
    school_name = db.Column(db.String(200))  # ឈ្មោះសាលា
    subject = db.Column(db.String(120))  # មុខវិជ្ជា
    photo_path = db.Column(db.String(255))  # រូបថត

    role = db.Column(db.String(20), default="user", nullable=False)  # 'admin' | 'user'
    is_active = db.Column(db.Boolean, default=True)
    chat_ai_enabled = db.Column(db.Boolean, default=True)  # True: AI auto-replies in support chat; False: admin only
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    generations = db.relationship("Generation", backref="user", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "gender": self.gender,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "school_name": self.school_name,
            "subject": self.subject,
            "photo_path": self.photo_path,
            "role": self.role,
            "is_active": self.is_active,
            "chat_ai_enabled": self.chat_ai_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Generation(db.Model):
    """ផ្ទុករបាយការណ៍ដែលបង្កើតដោយ AI (កិច្ចតែងការ, Slide, តេស្ត, កម្មវិធីសិក្សា)"""
    __tablename__ = "generations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    tool_type = db.Column(db.String(30), nullable=False)
    # 'lesson_plan' | 'slide' | 'test' | 'curriculum'

    style = db.Column(db.String(30), default="teal_light")  # slide theme: 'teal_light' | 'navy_dark' | 'moeys_formal' | 'playful'

    title = db.Column(db.String(255))
    teaching_method = db.Column(db.String(50))  # inquiry | bloom | student_centered
    lesson_date = db.Column(db.Date)
    lesson_hours = db.Column(db.Float)

    content_json = db.Column(db.Text)  # structured AI output, JSON string
    source_filename = db.Column(db.String(255))  # uploaded source doc/photo

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tool_type": self.tool_type,
            "style": self.style,
            "title": self.title,
            "teaching_method": self.teaching_method,
            "lesson_date": self.lesson_date.isoformat() if self.lesson_date else None,
            "lesson_hours": self.lesson_hours,
            "content_json": self.content_json,
            "source_filename": self.source_filename,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ChatMessage(db.Model):
    """
    Simple one-thread-per-user support chat between a teacher (user) and admin.
    `user_id` always identifies which teacher's conversation this belongs to,
    regardless of who actually sent the message (teacher or admin).
    """
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    sender_role = db.Column(db.String(10), nullable=False)  # 'user' | 'admin' | 'ai'
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # null for AI-authored messages
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "sender_role": self.sender_role,
            "sender_id": self.sender_id,
            "content": self.content,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SiteSettings(db.Model):
    """Single-row table holding editable 'About Us' content (admin-editable)."""
    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True)
    mission_text = db.Column(db.Text)
    contact_name = db.Column(db.String(150))
    contact_school = db.Column(db.String(200))
    contact_specialty = db.Column(db.String(150))
    contact_facebook = db.Column(db.String(150))
    contact_telegram = db.Column(db.String(150))
    contact_photo_url = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "mission_text": self.mission_text,
            "contact_name": self.contact_name,
            "contact_school": self.contact_school,
            "contact_specialty": self.contact_specialty,
            "contact_facebook": self.contact_facebook,
            "contact_telegram": self.contact_telegram,
            "contact_photo_url": self.contact_photo_url,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
