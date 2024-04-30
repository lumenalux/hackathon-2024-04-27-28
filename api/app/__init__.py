from flask import Flask

from app.config import Config
from app.presentation.http import api_v1, jwt, cors
from app.persistence.smtp import mail
from app.persistence.database import db, migrate
from app.persistence.oauth2 import oauth2


def init_app():
    app = Flask(__name__)
    app.register_blueprint(api_v1, url_prefix="/api/v1")

    app.config.from_object(Config())

    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        db.create_all()
        db.session.commit()
        db.session.close()

    mail.init_app(app)

    jwt.init_app(app)
    cors.init_app(app)
    oauth2.init_app(app)

    return app
