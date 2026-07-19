import os
from flask import Flask, send_from_directory
from config import Config
from extensions import db, bcrypt, jwt, cors


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["EXPORT_FOLDER"], exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # --- Manual CORS header fallback (handles some proxy/dev edge cases) ---
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        return response

    from routes.auth import auth_bp
    from routes.profile import profile_bp
    from routes.admin import admin_bp
    from routes.ai_tools import ai_bp
    from routes.export import export_bp
    from routes.chat import chat_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    app.register_blueprint(export_bp, url_prefix="/api/export")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.get("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.get("/exports/<path:filename>")
    def serve_export(filename):
        return send_from_directory(app.config["EXPORT_FOLDER"], filename, as_attachment=True)

    with app.app_context():
        db.create_all()
        _ensure_default_admin()

    return app


def _ensure_default_admin():
    """បង្កើត admin admin/admin1234 ដំបូង បើមិនទាន់មាន user ណាមួយ"""
    from models import User

    if User.query.count() == 0:
        admin = User(
            username="admin",
            full_name="សាលា Admin",
            role="admin",
        )
        admin.password_hash = bcrypt.generate_password_hash("admin1234").decode("utf-8")
        db.session.add(admin)
        db.session.commit()
        print("→ Default admin created: username='admin' password='admin1234' (please change it)")


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
