from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from models import db 

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def check():
        return {"status": "ok", "message": "HMS API running"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)