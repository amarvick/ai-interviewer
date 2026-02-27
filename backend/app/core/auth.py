from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import verify_token
from app.db.models.user import User

security = HTTPBearer(auto_error=False)

def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
):
    if creds is None:
        raise HTTPException(status_code=401, detail="Missing authentication credentials")

    user_id = verify_token(creds.credentials)

    if not user_id:
        token_preview = f"{creds.credentials[:12]}..." if creds.credentials else "<empty>"
        print(f"[AUTH] Invalid token received (preview={token_preview})")
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        print(f"[AUTH] Token resolved to user_id={user_id}, but user not found")
        raise HTTPException(status_code=401, detail="User not found")

    print(f"[AUTH] Authenticated user_id={user.id}")

    return user


def get_current_user_optional(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
):
    if creds is None:
        return None

    user_id = verify_token(creds.credentials)
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    return user
