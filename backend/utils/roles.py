from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from flask import jsonify
from models import User,Doctor, Patient

def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception as e:
                return jsonify({"msg": "Missing or invalid token", "error": str(e)}), 401

            claims = get_jwt()
            role = claims.get("role")
            if role not in allowed_roles:
                return jsonify({"msg": "Forbidden - insufficient role"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def get_doctor():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != "DOCTOR":
        return None
    return Doctor.query.filter_by(user_id=user.id).first()

def get_patient():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != "PATIENT":
        return None
    return Patient.query.filter_by(user_id=user.id).first()