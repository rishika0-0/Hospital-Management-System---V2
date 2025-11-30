# routes/patient.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date, timedelta

from models import db, User, Doctor, Patient, Department, Appointment, Treatment, DoctorAvailability
from utils.roles import role_required

patient_blueprint = Blueprint("patient", __name__, url_prefix="/api/patient")


def get_patient():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != "PATIENT":
        return None
    return Patient.query.filter_by(user_id=user.id).first()


@patient_blueprint.route("/dashboard", methods=["GET"])
@jwt_required()
@role_required("PATIENT")
def patient_dashboard():
    patient = get_patient()
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404

    today = date.today()

    upcoming = (
        Appointment.query
        .filter(
            Appointment.patient_id == patient.id,
            Appointment.date >= today
        )
        .order_by(Appointment.date, Appointment.start_time)
        .all()
    )

    past = (
        Appointment.query
        .filter(
            Appointment.patient_id == patient.id,
            Appointment.date < today
        )
        .order_by(Appointment.date.desc(), Appointment.start_time.desc())
        .all()
    )

    departments = Department.query.order_by(Department.name).all()

    def appt_to_dict(a):
        t = a.treatment
        return {
            "id": a.id,
            "date": a.date.isoformat(),
            "start_time": a.start_time.strftime("%H:%M"),
            "end_time": a.end_time.strftime("%H:%M"),
            "status": a.status_appointment,
            "doctor_id": a.doctor_id,
            "doctor_name": a.doctor.name if a.doctor else None,
            "diagnosis": t.diagnosis if t else None,
            "prescription": t.prescription if t else None,
        }

    return jsonify({
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "contact": patient.contact,
            "address": patient.address,
            "status": patient.status,
        },
        "upcoming": [appt_to_dict(a) for a in upcoming],
        "past": [appt_to_dict(a) for a in past],
        "departments": [
            {"id": d.id, "name": d.name, "description": d.description}
            for d in departments
        ]
    })


@patient_blueprint.route("/profile", methods=["GET", "PUT"])
@jwt_required()
@role_required("PATIENT")
def patient_profile():
    patient = get_patient()
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404

    user = User.query.get(patient.user_id)

    if request.method == "GET":
        return jsonify({
            "id": patient.id,
            "name": patient.name,
            "contact": patient.contact,
            "address": patient.address,
            "email": user.email if user else None,
        })

    data = request.get_json() or {}
    patient.name = data.get("name", patient.name)
    patient.contact = data.get("contact", patient.contact)
    patient.address = data.get("address", patient.address)

    new_email = data.get("email")
    if new_email and user:
        exists = User.query.filter(User.email == new_email, User.id != user.id).first()
        if exists:
            return jsonify({"msg": "Email already in use"}), 400
        user.email = new_email
        user.username = new_email

    new_password = data.get("password")
    if new_password and user:
        user.password = generate_password_hash(new_password)

    db.session.commit()
    return jsonify({"msg": "Profile updated"})


@patient_blueprint.route("/doctors", methods=["GET"])
@jwt_required()
@role_required("PATIENT")
def patient_search_doctors():
    q = request.args.get("q", "").strip()
    dept_id = request.args.get("department_id")

    query = Doctor.query.join(Department).filter(Doctor.status == True)

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Doctor.name.ilike(like),
                Department.name.ilike(like)
            )
        )

    if dept_id:
        query = query.filter(Doctor.specialization_id == dept_id)

    doctors = query.order_by(Doctor.name).all()

    result = []
    for d in doctors:
        result.append({
            "id": d.id,
            "name": d.name,
            "department_id": d.specialization_id,
            "department": d.department.name if d.department else None,
            "contact": d.contact,
            "availability": d.availability,
            "status": d.status,
        })

    return jsonify({"doctors": result})


@patient_blueprint.route("/doctors/<int:doctor_id>/slots", methods=["GET"])
@jwt_required()
@role_required("PATIENT")
def patient_doctor_slots(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    today = date.today()
    week_later = today + timedelta(days=7)

    db_slots = (
        DoctorAvailability.query
        .filter(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.date >= today,
            DoctorAvailability.date <= week_later,
            DoctorAvailability.is_available == True
        )
        .order_by(DoctorAvailability.date, DoctorAvailability.start_time)
        .all()
    )

    booked = (
        Appointment.query
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.date >= today,
            Appointment.date <= week_later,
            Appointment.status_appointment != "Cancelled"
        )
        .all()
    )

    booked_set = {(b.date, b.start_time, b.end_time) for b in booked}

    slots = []
    for s in db_slots:
        is_booked = (s.date, s.start_time, s.end_time) in booked_set
        slots.append({
            "slot_id": s.id,
            "weekday": s.date.strftime("%a"),
            "date": s.date.isoformat(),
            "start_time": s.start_time.strftime("%H:%M"),
            "end_time": s.end_time.strftime("%H:%M"),
            "is_booked": is_booked,
        })

    return jsonify({
        "doctor_id": doctor.id,
        "doctor_name": doctor.name,
        "slots": slots
    })


@patient_blueprint.route("/doctors/<int:doctor_id>/book", methods=["POST"])
@jwt_required()
@role_required("PATIENT")
def patient_book_appointment(doctor_id):
    patient = get_patient()
    if not patient:
        return jsonify({"msg": "Patient profile not found"}), 404

    doctor = Doctor.query.get_or_404(doctor_id)

    data = request.get_json() or {}
    slot_id = data.get("slot_id")
    if not slot_id:
        return jsonify({"msg": "slot_id required"}), 400

    selected = DoctorAvailability.query.get_or_404(slot_id)

    today = date.today()
    week_later = today + timedelta(days=7)
    if not (today <= selected.date <= week_later):
        return jsonify({"msg": "Slot not in allowed range"}), 400

    exists = Appointment.query.filter_by(
        doctor_id=doctor.id,
        date=selected.date,
        start_time=selected.start_time
    ).filter(Appointment.status_appointment != "Cancelled").first()

    if exists:
        return jsonify({"msg": "Slot already booked"}), 400

    exists_pt = Appointment.query.filter_by(
        patient_id=patient.id,
        date=selected.date,
        start_time=selected.start_time
    ).filter(Appointment.status_appointment != "Cancelled").first()

    if exists_pt:
        return jsonify({"msg": "You already have an appointment at this time"}), 400

    appt = Appointment(
        doctor_id=doctor.id,
        patient_id=patient.id,
        date=selected.date,
        start_time=selected.start_time,
        end_time=selected.end_time,
        status_appointment="Booked"
    )
    db.session.add(appt)
    db.session.commit()

    return jsonify({"msg": "Appointment booked", "appointment_id": appt.id}), 201


@patient_blueprint.route("/appointments/<int:appt_id>", methods=["GET"])
@jwt_required()
@role_required("PATIENT")
def patient_view_appointment(appt_id):
    patient = get_patient()
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404

    appt = Appointment.query.get_or_404(appt_id)
    if appt.patient_id != patient.id:
        return jsonify({"msg": "Not allowed to view this appointment"}), 403

    t = appt.treatment

    return jsonify({
        "id": appt.id,
        "date": appt.date.isoformat(),
        "start_time": appt.start_time.strftime("%H:%M"),
        "end_time": appt.end_time.strftime("%H:%M"),
        "status": appt.status_appointment,
        "doctor_id": appt.doctor_id,
        "doctor_name": appt.doctor.name if appt.doctor else None,
        "diagnosis": t.diagnosis if t else None,
        "prescription": t.prescription if t else None,
        "notes": t.notes if t else None,
    })


@patient_blueprint.route("/appointments/<int:appt_id>/cancel", methods=["PATCH"])
@jwt_required()
@role_required("PATIENT")
def patient_cancel_appointment(appt_id):
    patient = get_patient()
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404

    appt = Appointment.query.get_or_404(appt_id)
    if appt.patient_id != patient.id:
        return jsonify({"msg": "Not allowed to cancel this appointment"}), 403

    if appt.status_appointment == "Booked":
        appt.status_appointment = "Cancelled"
        db.session.commit()
        return jsonify({"msg": "Appointment cancelled"})
    else:
        return jsonify({"msg": "Only booked appointments can be cancelled"}), 400


@patient_blueprint.route("/appointments/<int:appt_id>/reschedule", methods=["PATCH"])
@jwt_required()
@role_required("PATIENT")
def patient_reschedule_appointment(appt_id):
    patient = get_patient()
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404

    appt = Appointment.query.get_or_404(appt_id)
    if appt.patient_id != patient.id:
        return jsonify({"msg": "Not allowed to reschedule this appointment"}), 403

    if appt.status_appointment != "Booked":
        return jsonify({"msg": "Only booked appointments can be rescheduled"}), 400

    doctor = appt.doctor

    data = request.get_json() or {}
    slot_id = data.get("slot_id")
    if not slot_id:
        return jsonify({"msg": "slot_id required"}), 400

    selected = DoctorAvailability.query.get_or_404(slot_id)

    other_appt = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date == selected.date,
        Appointment.start_time == selected.start_time,
        Appointment.id != appt.id,
        Appointment.status_appointment != "Cancelled"
    ).first()

    if other_appt:
        return jsonify({"msg": "Slot already booked"}), 400

    appt.date = selected.date
    appt.start_time = selected.start_time
    appt.end_time = selected.end_time
    db.session.commit()

    return jsonify({"msg": "Appointment rescheduled"})
