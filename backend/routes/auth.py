from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta
from models import db, User, Patient, Doctor

auth_blueprint = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_blueprint.route("/register", methods=["POST"])
def register():
    
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    name = data.get("name") or username

    if not username or not email or not password:
        return jsonify({"msg":"username, email and password are required"}), 400

    if User.query.filter((User.username==username) | (User.email==email)).first():
        return jsonify({"msg":"username or email already taken"}), 400

    hashed = generate_password_hash(password)
    user = User(username=username, email=email, password=hashed, role="PATIENT", status=True)
    db.session.add(user)
    db.session.flush()

    patient = Patient(user_id=user.id, name=name)
    db.session.add(patient)
    db.session.commit()

    return jsonify({"msg":"patient registered", "user_id": user.id}), 201


@auth_blueprint.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg":"email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.status:
        return jsonify({"msg":"invalid credentials"}), 401

    if not check_password_hash(user.password, password):
        return jsonify({"msg":"invalid credentials"}), 401

    addi_claims = {"role": user.role}
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=addi_claims,
        expires_delta=timedelta(hours=8)
    )

    redirect_map = {
        "ADMIN": "/admin/dashboard",
        "DOCTOR": "/doctor/dashboard",
        "PATIENT": "/patient/dashboard"
    }
    user_data = {"id": user.id, "username": user.username, "email": user.email, "role": user.role}
    return jsonify({
        "access_token": access_token,
        "user": user_data,
        "redirect": redirect_map.get(user.role, "/")
    }), 200
