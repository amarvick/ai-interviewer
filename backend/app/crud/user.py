from app.db.models.user import User
from app.core.security import hash_password

def get_user_by_email(db, email):
    return db.query(User).filter(
        User.email == email
    ).first()

def create_user(db, user):
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user