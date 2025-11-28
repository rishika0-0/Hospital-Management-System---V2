from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

def create_admin(username="admin", email="admin@hospital.com", password="admin123"):
    app = create_app()
    with app.app_context():
        existing = User.query.filter_by(role="ADMIN").first()
        if existing:
            print(f"[INFO] Admin already exists: username={existing.username}, email={existing.email}")
            return existing

        admin = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role="ADMIN",
            status=True,
        )
        db.session.add(admin)
        db.session.commit()
        print(f"[OK] Admin created: username={admin.username}, email={admin.email}")
        return admin

if __name__ == "__main__":
    create_admin()
