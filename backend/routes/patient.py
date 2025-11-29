# backend/routes/patient.py
from flask import Blueprint, jsonify
from utils.roles import role_required
from flask_jwt_extended import get_jwt_identity

patient_blueprint = Blueprint("patient", __name__, url_prefix="/api/patient")

@patient_blueprint.route("/me")
@role_required("PATIENT")
def patient_me():
    user_id = get_jwt_identity()
    from models import Patient
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return jsonify({"msg":"patient profile not found"}), 404
    return jsonify({
        "id": patient.id,
        "name": patient.name,
        "contact": patient.contact,
        "address": patient.address
    })
