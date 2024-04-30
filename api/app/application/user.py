from app.persistence.database import db
from app.domain.user import User


def delete_user(id_hash):
    user = None
    for query_user in User.query.all():
        if query_user.id_hash == id_hash:
            user = query_user
            break

    if not user:
        return 404

    db.session.delete(user)
    db.session.commit()

    return 200
