import uuid

from datetime import timedelta, datetime, timezone

from flask_jwt_extended import create_access_token, create_refresh_token

from app.persistence.database import db


class AnonymAuth():
    def __init__(self, db):
        self.db = db

    def register(self):
        expires_in = timedelta(hours=1)
        temp_user_id = str(uuid.uuid4())
        access_token = create_access_token(
            identity=temp_user_id,
            expires_delta=expires_in
        )

        refresh_token = create_refresh_token(identity=temp_user_id)

        expiration_time = datetime.now(timezone.utc) + expires_in

        return access_token, refresh_token, temp_user_id, expiration_time


anonym_auth = AnonymAuth(db)
