from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

# Admin/Doctor/Patient
class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    role=db.Column(db.String(20),nullable=False, index=True)
    status=db.Column(db.Boolean, default=True, nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    #relationship (User-Doctor 1:1)
    doctor=db.relationship("Doctor",backref="user",uselist=False,cascade="all, delete-orphan")
    patient = db.relationship("Patient", backref="user", uselist=False, cascade="all, delete-orphan")

    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# Department
class Department(db.Model):
    __tablename__="department"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    date_created= db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
     #relationships (Department-Doctor 1:N)
    doctors = db.relationship("Doctor", backref="department", lazy=True)
    
    def __repr__(self):
        return f"<Department {self.name}>"


# Doctor
class Doctor(db.Model):
    __tablename__="doctor"

    id = db.Column(db.Integer, primary_key=True)
    #linking to user table
    user_id=db.Column(db.Integer, db.ForeignKey("user.id"),nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    specialization_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    availability = db.Column(db.String(500), nullable=True)
    contact = db.Column(db.String(20), nullable=True)
    
    status = db.Column(db.Boolean, default=True, nullable=False)  
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    #relationships (Doctor-Appoint 1:N)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    slot_availability = db.relationship('DoctorAvailability', backref='doctor', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Doctor {self.name} - (user_id={self.user_id})>"


# Patient
class Patient(db.Model):
    __tablename__="patient"

    id=db.Column(db.Integer, primary_key=True)

    #linking to user table
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"),nullable=False,unique=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    contact = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Boolean, default=True, nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    #relationship (1:N)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

    def __repr__(self):
        return f"<Patient {self.name} - (user_id={self.user_id})>"


# DoctorAvailability
class DoctorAvailability(db.Model):
    __tablename__='doctor_availability'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    is_available = db.Column(db.Boolean, default=True, nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # to ensure a doctor not have duplicate identical slots
    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'date', 'start_time', 'end_time', name='uix_doc_slot'),
    )

    def __repr__(self):
        return f"<Avail Doctor:{self.doctor_id} {self.date} {self.start_time}-{self.end_time}>"

# Appointment
class Appointment(db.Model):
    __tablename__="appointment"

    id = db.Column(db.Integer, primary_key=True)

    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)

    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    status_appointment = db.Column(db.String(20), default='Booked', nullable=False, index=True)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    #relationship (1:1)
    treatment = db.relationship('Treatment', backref='appointment', uselist=False, cascade="all, delete-orphan")
    
    # Prevent multiple appointments at same date & time for the same doctor
    __table_args__ = (db.UniqueConstraint("doctor_id","date","start_time",name="uix_doctor_timeslot",),
    )

    def __repr__(self):
        return f"<Appointment Dr:{self.doctor_id} Pt:{self.patient_id} {self.date} {self.start_time}>"

# Treatment 
class Treatment(db.Model):
    __tablename__="treatment"

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False, unique=True, index=True)
    diagnosis = db.Column(db.Text, nullable=True)
    prescription = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Treatment appt:{self.appointment_id}>"
