from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from models import db 

migrate = Migrate()
jwt=JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from routes.auth import auth_blueprint as auth
    from routes.admin import admin_blueprint as admin
    from routes.doctor import doctor_blueprint as doc
    from routes.patient import patient_blueprint as patient

    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(doc)
    app.register_blueprint(patient)

    @app.route("/api/health")
    def check():
        return {"status": "ok", "message": "HMS API running"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)