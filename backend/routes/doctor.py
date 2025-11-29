from flask import Blueprint, jsonify
from utils.roles import role_required
from flask_jwt_extended import get_jwt_identity

doctor_blueprint = Blueprint("doctor", __name__, url_prefix="/api/doctor")

@doctor_blueprint.route("/me")
@role_required("DOCTOR")
def doctor_me():
    user_id = get_jwt_identity()

    from models import Doctor
    doc = Doctor.query.filter_by(user_id=user_id).first()
    if not doc:
        return jsonify({"msg":"doctor profile not found"}), 404
    return jsonify({
        "id": doc.id,
        "name": doc.name,
        "contact": doc.contact,
        "specialization_id": doc.specialization_id
    })
