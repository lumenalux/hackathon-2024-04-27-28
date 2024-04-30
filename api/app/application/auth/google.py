from datetime import timedelta, datetime, timezone

from flask_jwt_extended import create_access_token

from app.config import OAuthConfig
from app.domain.user import GoogleAuthenticationEntity, User
from app.persistence.database import db
from app.persistence.oauth2 import oauth2


class GoogleAuth:
    def __init__(self,
                 db,
                 oauth2):
        self.db = db
        print("GoogleAuth init")
        oauth2.register(
            name='google',
            client_id=OAuthConfig.GOOGLE_CLIENT_ID,
            client_secret=OAuthConfig.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',  # noqa
            client_kwargs={
                'scope': 'openid email profile'
            }
        )

        self.oauth2 = oauth2

    def _create_new_auth(self, google_sub_id):
        new_user = User()
        self.db.session.add(new_user)
        self.db.session.flush()

        google_auth = GoogleAuthenticationEntity(
            sub_id=google_sub_id,
            user=new_user
        )

        self.db.session.add(google_auth)
        self.db.session.commit()
        self.db.session.flush()

        return google_auth

    def register(self):
        token = self.oauth2.google.authorize_access_token()
        google_sub_id = token['userinfo']['sub']

        google_auth = GoogleAuthenticationEntity.query.filter_by(
            sub_id=google_sub_id).first()

        if not google_auth:
            google_auth = self._create_new_auth(google_sub_id)

        expires_in = timedelta(hours=1)
        user_id_hash = google_auth.user.id_hash

        access_token = create_access_token(
            identity=user_id_hash,
            expires_delta=expires_in
        )

        refresh_token = create_access_token(identity=user_id_hash)

        expiration_time = datetime.now(timezone.utc) + expires_in

        return access_token, refresh_token, user_id_hash, expiration_time


google_auth = GoogleAuth(db, oauth2)
