"""
Profile photo storage. Uses Cloudinary (persistent, free tier) when
CLOUDINARY_URL is set in the environment; otherwise falls back to saving
on local disk (fine for local dev, but files are lost on Render restarts
since the free tier has no persistent disk).
"""
import os
import uuid
from werkzeug.utils import secure_filename


def _cloudinary_configured():
    return bool(os.environ.get("CLOUDINARY_URL"))


def upload_avatar(file_storage, upload_folder):
    """
    file_storage: a Werkzeug FileStorage (from request.files)
    upload_folder: local uploads dir, used only for the fallback path.
    Returns: a string to store in User.photo_path — either a full Cloudinary
             URL (starts with "http") or a local filename.
    """
    if _cloudinary_configured():
        import cloudinary.uploader

        result = cloudinary.uploader.upload(
            file_storage,
            folder="ai-lesson-tool/avatars",
            resource_type="image",
            overwrite=True,
        )
        return result["secure_url"]

    # Fallback: local disk (existing behavior)
    fname = f"{uuid.uuid4().hex}_{secure_filename(file_storage.filename)}"
    file_storage.save(os.path.join(upload_folder, fname))
    return fname
