from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt
from models import db, User, Doctor, Patient, Appointment, Department
from utils.roles import role_required
from datetime import date

admin_blueprint = Blueprint("admin", __name__, url_prefix="/api/admin")

def require_admin():
    claims = get_jwt()  
    if claims.get("role") != "ADMIN":
        return None
    return claims

@admin_blueprint.route("/dashboard", methods=["GET"])
@jwt_required()
def admin_dashboard():
    identity = require_admin()
    if not identity:
        return jsonify({"msg": "Admin access required"}), 403

    total_doctors = Doctor.query.filter_by(status=True).count()
    total_patients = Patient.query.filter_by(status=True).count()
    total_appointments = Appointment.query.count()

    today = date.today()
    upcoming = (
        Appointment.query
        .filter(Appointment.date >= today)
        .order_by(Appointment.date, Appointment.start_time)
        .limit(10)
        .all()
    )

    upcoming_data = []
    for a in upcoming:
        upcoming_data.append({
            "id": a.id,
            "date": a.date.isoformat(),
            "start_time": a.start_time.strftime("%H:%M"),
            "end_time": a.end_time.strftime("%H:%M"),
            "status": a.status_appointment,
            "doctor_id": a.doctor_id,
            "doctor_name": a.doctor.name if a.doctor else None,
            "patient_id": a.patient_id,
            "patient_name": a.patient.name if a.patient else None,
        })

    return jsonify({
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "upcoming_appointments": upcoming_data,
    })

@admin_blueprint.route("/doctors", methods=["POST"])
@jwt_required()
def admin_add_doctor():
    identity = require_admin()
    if not identity:
        return jsonify({"msg": "Admin access required"}), 403

    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    department_id = data.get("department_id")
    contact = data.get("contact")
    availability = data.get("availability") 

    if not all([name, email, password, department_id]):
        return jsonify({"msg": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already in use"}), 400

    user = User(
        username=email,
        email=email,
        password=generate_password_hash(password),
        role="DOCTOR",
        status=True,
    )
    db.session.add(user)
    db.session.flush() 

    doc = Doctor(
        user_id=user.id,
        name=name,
        specialization_id=department_id,
        contact=contact,
        availability=availability,
        status=True,
    )
    db.session.add(doc)
    db.session.commit()

    try:
        from app import regenerate_availability_slots
        regenerate_availability_slots(doc)
    except Exception as e:
        print("Slot generation error:", e)

    return jsonify({
        "msg": "Doctor created",
        "doctor": {
            "id": doc.id,
            "name": doc.name,
            "email": user.email,
            "department_id": doc.specialization_id,
            "contact": doc.contact,
            "status": doc.status,
            "availability": doc.availability,
        }
    }), 201

@admin_blueprint.route("/doctors/<int:doctor_id>", methods=["PUT"])
@jwt_required()
def admin_update_doctor(doctor_id):
    identity = require_admin()
    if not identity:
        return jsonify({"msg": "Admin access required"}), 403

    doc = Doctor.query.get_or_404(doctor_id)
    user = doc.user 

    data = request.get_json() or {}
    old_avail = doc.availability

    doc.name = data.get("name", doc.name)
    doc.contact = data.get("contact", doc.contact)
    doc.specialization_id = data.get("department_id", doc.specialization_id)
    doc.availability = data.get("availability", doc.availability)

    new_email = data.get("email")
    if new_email and new_email != user.email:
        if User.query.filter(User.email == new_email, User.id != user.id).first():
            return jsonify({"msg": "Email already used by another user"}), 400
        user.email = new_email
        user.username = new_email 

    new_password = data.get("password")
    if new_password:
        user.password = generate_password_hash(new_password)

    db.session.commit()

    if doc.availability != old_avail:
        try:
            from app import regenerate_availability_slots
            regenerate_availability_slots(doc)
        except Exception as e:
            print("Slot regen error:", e)

    return jsonify({
        "msg": "Doctor updated",
        "doctor": {
            "id": doc.id,
            "name": doc.name,
            "email": user.email,
            "department_id": doc.specialization_id,
            "contact": doc.contact,
            "status": doc.status,
            "availability": doc.availability,
        }
    })

@admin_blueprint.route("/doctors", methods=["GET"])
@jwt_required()
def admin_list_doctors():
    identity = require_admin()
    if not identity:
        return jsonify({"msg": "Admin access required"}), 403

    q = request.args.get("q", "").strip()
    dept_id = request.args.get("department_id")

    query = Doctor.query.join(Department)

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
            "department": d.department.name if d.department else None,
            "department_id": d.specialization_id,
            "contact": d.contact,
            "status": d.status,
        })

    return jsonify({"doctors": result})

#search patients
@admin_blueprint.route("/patients", methods=["GET"])
@jwt_required()
def admin_list_patients():
    identity = require_admin()
    if not identity:
        return jsonify({"msg": "Admin access required"}), 403

    q = request.args.get("q", "").strip()

    query = Patient.query

    if q:
        conditions = [
        Patient.name.ilike(f"%{q}%"),
        Patient.contact.ilike(f"%{q}%"),
        User.email.ilike(f"%{q}%")
    ]
    
        # if hasattr(Patient, "email"):
        #     conditions.append(Patient.email.ilike(f"%{q}%"))

        if q.isdigit():
            conditions.append(Patient.id == int(q))

        query = query.filter(db.or_(*conditions))

    patients = query.order_by(Patient.name).all()

    result = []
    for p in patients:
        result.append({
            "id": p.id,
            "name": p.name,
            "contact": p.contact,
            "status": p.status,
        })

    return jsonify({"patients": result})

#view appts
@admin_blueprint.route("/appointments", methods=["GET"])
@jwt_required()
def admin_appointments():
    identity = require_admin()
    if not identity:
        return jsonify({"msg": "Admin access required"}), 403

    filter_type = request.args.get("filter", "upcoming")
    today = date.today()

    base_query = Appointment.query

    if filter_type == "past":
        base_query = base_query.filter(Appointment.date < today)
        base_query = base_query.order_by(Appointment.date.desc(), Appointment.start_time.desc())
    else:
        base_query = base_query.filter(Appointment.date >= today)
        base_query = base_query.order_by(Appointment.date, Appointment.start_time)

    appts = base_query.all()

    result = []
    for a in appts:
        result.append({
            "id": a.id,
            "date": a.date.isoformat(),
            "start_time": a.start_time.strftime("%H:%M"),
            "end_time": a.end_time.strftime("%H:%M"),
            "status": a.status_appointment,
            "doctor_id": a.doctor_id,
            "doctor_name": a.doctor.name if a.doctor else None,
            "patient_id": a.patient_id,
            "patient_name": a.patient.name if a.patient else None,
        })

    return jsonify({"appointments": result})

@admin_blueprint.route("/appointments/<int:appt_id>/status", methods=["PATCH"])
@jwt_required()
def admin_change_appointment_status(appt_id):
    identity = require_admin()
    if not identity:
        return jsonify({"msg": "Admin access required"}), 403

    appt = Appointment.query.get_or_404(appt_id)
    data = request.get_json() or {}
    new_status = data.get("status")

    if new_status not in ["Booked", "Completed", "Cancelled"]:
        return jsonify({"msg": "Invalid status"}), 400

    appt.status_appointment = new_status
    db.session.commit()

    return jsonify({"msg": "Status updated", "appointment_id": appt.id, "status": appt.status_appointment})

#active/blacklist
@admin_blueprint.route("/doctors/<int:doctor_id>/toggle", methods=["PATCH"])
@jwt_required()
def admin_toggle_doctor(doctor_id):
    identity = require_admin()
    if not identity:
        return jsonify({"msg": "Admin access required"}), 403

    doc = Doctor.query.get_or_404(doctor_id)
    doc.status = not doc.status
    if doc.user:
        doc.user.status = doc.status
    db.session.commit()

    return jsonify({
        "msg": "Doctor status toggled",
        "doctor_id": doc.id,
        "status": doc.status
    })

@admin_blueprint.route("/patients/<int:patient_id>/toggle", methods=["PATCH"])
@jwt_required()
def admin_toggle_patient(patient_id):
    identity = require_admin()
    if not identity:
        return jsonify({"msg": "Admin access required"}), 403

    p = Patient.query.get_or_404(patient_id)
    p.status = not p.status
    db.session.commit()

    return jsonify({
        "msg": "Patient status toggled",
        "patient_id": p.id,
        "status": p.status
    })

#deletion of doc/patient
@admin_blueprint.route("/doctors/<int:doctor_id>", methods=["DELETE"])
@jwt_required()
def admin_delete_doctor(doctor_id):
    identity = require_admin()
    if not identity:
        return jsonify({"msg": "Admin access required"}), 403

    doc = Doctor.query.get_or_404(doctor_id)
    has_appointments = Appointment.query.filter_by(doctor_id=doctor_id).count() > 0
    if has_appointments:
        return jsonify({"msg": "Cannot delete doctor with existing appointments"}), 400

    db.session.delete(doc)
    db.session.commit()
    return jsonify({"msg": "Doctor deleted", "doctor_id": doctor_id})

@admin_blueprint.route("/patients/<int:patient_id>", methods=["DELETE"])
@jwt_required()
def admin_delete_patient(patient_id):
    identity = require_admin()
    if not identity:
        return jsonify({"msg": "Admin access required"}), 403

    p = Patient.query.get_or_404(patient_id)
    has_appointments = Appointment.query.filter_by(patient_id=patient_id).count() > 0
    if has_appointments:
        return jsonify({"msg": "Cannot delete patient with existing appointments"}), 400

    db.session.delete(p)
    db.session.commit()
    return jsonify({"msg": "Patient deleted", "patient_id": patient_id})