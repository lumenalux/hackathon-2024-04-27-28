import hashlib

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property

from app.persistence.database import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    id_hash = db.Column(db.String(128), unique=True,
                        nullable=False, index=True)

    authentication = db.relationship(
        'IAuthenticationEntity', back_populates='user', uselist=False)

    @hybrid_property
    def id_hash(self):  # noqa
        return hashlib.sha256(str(self.id).encode('utf-8')).hexdigest()

    @id_hash.expression
    def id_hash(cls):
        return hashlib.sha256(
            str(cls.id).cast(db.String).encode('utf-8')).hexdigest()


class IAuthenticationEntity(db.Model):
    __tablename__ = 'authentication_entities'
    id = db.Column(db.Integer, primary_key=True)
    registered = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'authentication_entity',
        'polymorphic_on': type
    }

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='authentication')


class EmailAuthenticationEntity(IAuthenticationEntity):
    __tablename__ = 'email_authentication_entities'
    id = db.Column(db.Integer, db.ForeignKey(
        'authentication_entities.id'), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Column to store the password hash
    password_hash = db.Column(db.String(128))
    is_confirmed = db.Column(db.Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'email_authentication_entity',
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class GoogleAuthenticationEntity(IAuthenticationEntity):
    __tablename__ = 'google_authentication_entities'
    id = db.Column(db.Integer, db.ForeignKey(
        'authentication_entities.id'), primary_key=True)
    sub_id = db.Column(db.String(32), unique=True, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'google_authentication_entity',
    }
