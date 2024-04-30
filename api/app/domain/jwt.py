from app.persistence.database import db


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(1000), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
