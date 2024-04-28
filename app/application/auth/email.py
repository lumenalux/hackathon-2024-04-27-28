from datetime import timedelta, datetime, timezone

from flask import url_for
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from app.persistence.database import db
from app.domain.user import EmailAuthenticationEntity, User


class EmailAuth:
    def __init__(self,
                 db,
                 salt='email-confirm',
                 password_reset_salt='password-reset'):
        self.db = db
        self.salt = salt
        self.password_reset_salt = password_reset_salt
        self.url_serializer = URLSafeTimedSerializer(salt)

    def authorize(self, email, password):
        user_auth = EmailAuthenticationEntity.query.filter_by(
            email=email).first()

        if not user_auth or not user_auth.check_password(password):
            return None, None, None, None

        if not user_auth.is_confirmed:
            return None, None, None, None

        expires_in = timedelta(hours=1)
        user_id_hash = user_auth.user.id_hash

        access_token = create_access_token(
            identity=user_id_hash,
            expires_delta=expires_in
        )

        refresh_token = create_refresh_token(identity=user_id_hash)

        expiration_time = datetime.now(timezone.utc) + expires_in

        return access_token, refresh_token, user_id_hash, expiration_time

    def register(self, email, password):
        if not email or not password:
            return None, 400

        if EmailAuthenticationEntity.query.filter_by(email=email).first():
            return None, 409

        new_user = User()
        self.db.session.add(new_user)
        self.db.session.flush()  # Flush to assign an ID before commit

        password_hash = generate_password_hash(password)
        new_user_auth = EmailAuthenticationEntity(
            email=email,
            password_hash=password_hash,
            is_confirmed=False,
            user=new_user
        )

        self.db.session.add(new_user_auth)
        self.db.session.commit()

        token = self.url_serializer.dumps(email, salt=self.salt)
        confirm_url = url_for('api_v1.email_verification',
                              token=token, _external=True)

        return confirm_url, 201

    def confirm_email(self, token):
        try:
            email = self.url_serializer.loads(
                token, salt=self.salt, max_age=3600)
        except SignatureExpired:
            return 400

        user_auth = EmailAuthenticationEntity.query.filter_by(
            email=email).first_or_404()

        if not user_auth.is_confirmed:
            user_auth.is_confirmed = True
            self.db.session.commit()

        return 200

    def forgot_password(self, email):
        user_auth = EmailAuthenticationEntity.query.filter_by(
            email=email).first()
        if not user_auth:
            return None, 404

        token = self.url_serializer.dumps(email, salt=self.password_reset_salt)
        reset_url = url_for('api_v1.email_reset_password',
                            token=token, _external=True)

        return reset_url, 200

    def reset_password(self, token, new_password):
        try:
            email = self.url_serializer.loads(
                token, salt=self.password_reset_salt, max_age=3600)
        except SignatureExpired:
            return 400

        user_auth = EmailAuthenticationEntity.query.filter_by(
            email=email).first_or_404()
        user_auth.password_hash = generate_password_hash(new_password)
        self.db.session.commit()

        return 200

    def update_password(self, id_hash, new_password):
        user = None
        for query_user in User.query.all():
            if query_user.id_hash == id_hash:
                user = query_user
                break

        if not user:
            return 404

        user_auth = EmailAuthenticationEntity.query.filter_by(
            user_id=user.id).first()

        if not user_auth:
            return 404

        if new_password:
            user_auth.password_hash = generate_password_hash(
                new_password)
            self.db.session.add(user_auth)
            self.db.session.commit()

        return 200

    def update_email(self, id_hash, new_email):
        user = None
        for query_user in User.query.all():
            if query_user.id_hash == id_hash:
                user = query_user
                break

        if not user:
            return 404

        user_auth = EmailAuthenticationEntity.query.filter_by(
            user_id=user.id).first()

        if not user_auth:
            return 404

        if new_email:
            user_auth.email = new_email
            self.db.session.add(user_auth)
            self.db.session.commit()

        return 200


email_auth = EmailAuth(db)
