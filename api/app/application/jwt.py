from datetime import datetime, timezone

from app.domain.jwt import TokenBlocklist
from app.persistence.database import db


def is_token_blocklisted(jti):
    return TokenBlocklist.query.filter_by(jti=jti).scalar() is not None


def add_token_to_blocklist(jti):
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
