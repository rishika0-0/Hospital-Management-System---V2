from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import date, timedelta

from models import db, User, Doctor, Patient, Appointment, Treatment, DoctorAvailability
from utils.roles import role_required
from flask_jwt_extended import get_jwt_identity

doctor_blueprint = Blueprint("doctor", __name__, url_prefix="/api/doctor")


def get_doctor():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != "DOCTOR":
        return None
    return Doctor.query.filter_by(user_id=user.id).first()


@doctor_blueprint.route("/dashboard", methods=["GET"])
@jwt_required()
@role_required("DOCTOR")
def doctor_dashboard():
    doctor = get_doctor()
    if not doctor:
        return jsonify({"msg": "Doctor not found"}), 404

    today = date.today()
    week_later = today + timedelta(days=7)

    weekly_appts = (
        Appointment.query
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.date >= today,
            Appointment.date <= week_later,
        )
        .order_by(Appointment.date, Appointment.start_time)
        .all()
    )

    todays = [a for a in weekly_appts if a.date == today]

    def appt_to_dict(a):
        return {
            "id": a.id,
            "date": a.date.isoformat(),
            "start_time": a.start_time.strftime("%H:%M"),
            "end_time": a.end_time.strftime("%H:%M"),
            "status": a.status_appointment,
            "patient_id": a.patient_id,
            "patient_name": a.patient.name if a.patient else None,
        }

    return jsonify({
        "doctor_id": doctor.id,
        "doctor_name": doctor.name,
        "today": [appt_to_dict(a) for a in todays],
        "week": [appt_to_dict(a) for a in weekly_appts],
    })


@doctor_blueprint.route("/patients", methods=["GET"])
@jwt_required()
@role_required("DOCTOR")
def doctor_assigned_patients():
    doctor = get_doctor()
    if not doctor:
        return jsonify({"msg": "Doctor profile not found"}), 404

    appts = Appointment.query.filter_by(doctor_id=doctor.id).all()
    patient_ids = {a.patient_id for a in appts}
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()

    result = []
    for p in patients:
        result.append({
            "id": p.id,
            "name": p.name,
            "contact": p.contact,
            "status": p.status,
        })
    return jsonify({"patients": result})


@doctor_blueprint.route("/appointments/<int:appt_id>", methods=["GET"])
@jwt_required()
@role_required("DOCTOR")
def doctor_get_appointment(appt_id):
    doctor = get_doctor()
    if not doctor:
        return jsonify({"msg": "Doctor not found"}), 404

    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != doctor.id:
        return jsonify({"msg": "Not allowed to access this appointment"}), 403

    treatment = appt.treatment

    return jsonify({
        "id": appt.id,
        "date": appt.date.isoformat(),
        "start_time": appt.start_time.strftime("%H:%M"),
        "end_time": appt.end_time.strftime("%H:%M"),
        "status": appt.status_appointment,
        "patient_id": appt.patient_id,
        "patient_name": appt.patient.name if appt.patient else None,
        "treatment": {
            "diagnosis": treatment.diagnosis if treatment else None,
            "prescription": treatment.prescription if treatment else None,
            "notes": treatment.notes if treatment else None,
        } if treatment else None
    })


@doctor_blueprint.route("/appointments/<int:appt_id>", methods=["PATCH"])
@jwt_required()
@role_required("DOCTOR")
def doctor_update_appointment(appt_id):
    
    doctor = get_doctor()
    if not doctor:
        return jsonify({"msg": "Doctor not found"}), 404

    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != doctor.id:
        return jsonify({"msg": "Not allowed to modify this appointment"}), 403

    data = request.get_json() or {}

    status = data.get("status")
    if status in ["Booked", "Completed", "Cancelled"]:
        appt.status_appointment = status

    diagnosis = data.get("diagnosis")
    prescription = data.get("prescription")
    notes = data.get("notes")

    if diagnosis is not None or prescription is not None or notes is not None:
        if appt.treatment:
            if diagnosis is not None:
                appt.treatment.diagnosis = diagnosis
            if prescription is not None:
                appt.treatment.prescription = prescription
            if notes is not None:
                appt.treatment.notes = notes
        else:
            treatment = Treatment(
                appointment_id=appt.id,
                diagnosis=diagnosis,
                prescription=prescription,
                notes=notes
            )
            db.session.add(treatment)

    db.session.commit()

    return jsonify({"msg": "Appointment updated"})


@doctor_blueprint.route("/patients/<int:patient_id>/history", methods=["GET"])
@jwt_required()
@role_required("DOCTOR")
def doctor_patient_history(patient_id):
    doctor = get_doctor()
    if not doctor:
        return jsonify({"msg": "Doctor profile not found"}), 404

    patient = Patient.query.get_or_404(patient_id)

    appts = (
        Appointment.query
        .filter_by(patient_id=patient.id)
        .order_by(Appointment.date.desc(), Appointment.start_time.desc())
        .all()
    )

    result = []
    for a in appts:
        t = a.treatment
        result.append({
            "id": a.id,
            "date": a.date.isoformat(),
            "start_time": a.start_time.strftime("%H:%M"),
            "end_time": a.end_time.strftime("%H:%M"),
            "status": a.status_appointment,
            "doctor_id": a.doctor_id,
            "doctor_name": a.doctor.name if a.doctor else None,
            "diagnosis": t.diagnosis if t else None,
            "prescription": t.prescription if t else None,
            "notes": t.notes if t else None,
        })

    return jsonify({
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "contact": patient.contact,
            "status": patient.status,
        },
        "appointments": result
    })


@doctor_blueprint.route("/availability", methods=["GET"])
@jwt_required()
@role_required("DOCTOR")
def doctor_get_availability():
    doctor = get_doctor()
    if not doctor:
        return jsonify({"msg": "Doctor profile not found"}), 404

    return jsonify({
        "doctor_id": doctor.id,
        "availability": doctor.availability
    })


@doctor_blueprint.route("/availability", methods=["PUT"])
@jwt_required()
@role_required("DOCTOR")
def doctor_update_availability():
    
    from app import regenerate_availability_slots 

    doctor = get_doctor()
    if not doctor:
        return jsonify({"msg": "Doctor not found"}), 404

    data = request.get_json() or {}
    new_avail = data.get("availability")

    if not new_avail:
        return jsonify({"msg": "Availability string required"}), 400

    doctor.availability = new_avail
    db.session.commit()

    regenerate_availability_slots(doctor)

    return jsonify({"msg": "Availability updated", "availability": doctor.availability})
