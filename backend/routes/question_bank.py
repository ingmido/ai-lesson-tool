import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import QuestionBankItem, Generation

qbank_bp = Blueprint("qbank", __name__)


@qbank_bp.get("")
@jwt_required()
def list_questions():
    user_id = int(get_jwt_identity())
    q = QuestionBankItem.query.filter_by(user_id=user_id)

    search = request.args.get("search", "").strip()
    subject = request.args.get("subject", "").strip()
    tag = request.args.get("tag", "").strip()

    if search:
        q = q.filter(QuestionBankItem.question_text.ilike(f"%{search}%"))
    if subject:
        q = q.filter(QuestionBankItem.subject == subject)
    if tag:
        q = q.filter(QuestionBankItem.tags.ilike(f"%{tag}%"))

    items = q.order_by(QuestionBankItem.created_at.desc()).all()
    return jsonify([i.to_dict() for i in items])


@qbank_bp.get("/subjects")
@jwt_required()
def list_subjects():
    """Distinct subjects the teacher has saved, for a filter dropdown."""
    user_id = int(get_jwt_identity())
    rows = (
        db.session.query(QuestionBankItem.subject)
        .filter(QuestionBankItem.user_id == user_id, QuestionBankItem.subject.isnot(None))
        .distinct()
        .all()
    )
    return jsonify(sorted({r[0] for r in rows if r[0]}))


@qbank_bp.post("")
@jwt_required()
def create_question():
    user_id = int(get_jwt_identity())
    data = request.get_json(force=True) or {}

    question_text = (data.get("question_text") or "").strip()
    if not question_text:
        return jsonify({"error": "សូមបញ្ចូលខ្លឹមសារសំណួរ"}), 400

    choices = data.get("choices")
    item = QuestionBankItem(
        user_id=user_id,
        subject=data.get("subject"),
        grade=data.get("grade"),
        question_type=data.get("question_type", "mcq"),
        question_text=question_text,
        choices_json=json.dumps(choices, ensure_ascii=False) if choices else None,
        answer=data.get("answer"),
        tags=",".join(data.get("tags", [])) if isinstance(data.get("tags"), list) else data.get("tags"),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@qbank_bp.delete("/<int:item_id>")
@jwt_required()
def delete_question(item_id):
    user_id = int(get_jwt_identity())
    item = QuestionBankItem.query.get_or_404(item_id)
    if item.user_id != user_id:
        return jsonify({"error": "គ្មានសិទ្ធិលុប"}), 403
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "លុបជោគជ័យ"})


@qbank_bp.post("/import/<int:gen_id>")
@jwt_required()
def import_from_generation(gen_id):
    """Pull every question out of an AI-generated test into the bank."""
    user_id = int(get_jwt_identity())
    gen = Generation.query.get_or_404(gen_id)
    if gen.user_id != user_id:
        return jsonify({"error": "គ្មានសិទ្ធិចូលមើល"}), 403
    if gen.tool_type != "test":
        return jsonify({"error": "អាចទាញចូលបានតែពី tool តេស្តប៉ុណ្ណោះ"}), 400

    data = request.get_json(force=True) or {}
    subject = data.get("subject", "")
    grade = data.get("grade", "")
    tags = data.get("tags", "")

    content = json.loads(gen.content_json) if gen.content_json else {}
    saved = []
    for section in content.get("sections", []):
        for q in section.get("questions", []):
            item = QuestionBankItem(
                user_id=user_id,
                subject=subject,
                grade=grade,
                question_type="mcq" if q.get("choices") else "short",
                question_text=q.get("question", ""),
                choices_json=json.dumps(q.get("choices"), ensure_ascii=False) if q.get("choices") else None,
                answer=q.get("answer", ""),
                tags=tags,
            )
            db.session.add(item)
            saved.append(item)
    db.session.commit()
    return jsonify({"saved_count": len(saved), "items": [i.to_dict() for i in saved]}), 201


@qbank_bp.post("/build-test")
@jwt_required()
def build_test():
    """Assemble a new test Generation from selected bank question IDs — no AI call needed."""
    user_id = int(get_jwt_identity())
    data = request.get_json(force=True) or {}
    ids = data.get("ids", [])
    title = data.get("title") or "តេស្តពីធនាគារសំណួរ"

    if not ids:
        return jsonify({"error": "សូមជ្រើសរើសសំណួរយ៉ាងហោចណាស់មួយ"}), 400

    items = QuestionBankItem.query.filter(
        QuestionBankItem.id.in_(ids), QuestionBankItem.user_id == user_id
    ).all()
    items_by_id = {i.id: i for i in items}
    ordered = [items_by_id[i] for i in ids if i in items_by_id]

    questions = []
    for i, item in enumerate(ordered, start=1):
        q = {"number": i, "question": item.question_text, "answer": item.answer}
        d = item.to_dict()
        if d["choices"]:
            q["choices"] = d["choices"]
        questions.append(q)

    content = {
        "title": title,
        "instructions": "សូមឆ្លើយសំណួរខាងក្រោមទាំងអស់។",
        "duration": "",
        "sections": [{"section_title": "សំណួរ", "questions": questions}],
    }

    gen = Generation(
        user_id=user_id,
        tool_type="test",
        title=title,
        content_json=json.dumps(content, ensure_ascii=False),
    )
    db.session.add(gen)
    db.session.commit()

    return jsonify({"generation": gen.to_dict(), "content": content}), 201
