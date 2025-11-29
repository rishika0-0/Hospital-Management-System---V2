from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, User, Doctor
from utils.roles import role_required

admin_blueprint = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_blueprint.route("/doctors", methods=["POST"])
@role_required("ADMIN")
def add_doctor():
    
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or "changeme123"
    name = data.get("name") or username
    specialization_id = data.get("specialization_id")
    contact = data.get("contact")

    if not username or not email or not specialization_id:
        return jsonify({"msg":"username, email and specialization_id are required"}), 400

    if User.query.filter((User.username==username) | (User.email==email)).first():
        return jsonify({"msg":"user exists"}), 400

    hashed = generate_password_hash(password)
    user = User(username=username, email=email, password=hashed, role="DOCTOR", status=True)
    db.session.add(user)
    db.session.flush() 

    doctor = Doctor(user_id=user.id, name=name, specialization_id=specialization_id, contact=contact)
    db.session.add(doctor)
    db.session.commit()

    return jsonify({"msg":"doctor created", "doctor_id": doctor.id}), 201
