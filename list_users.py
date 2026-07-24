from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()

for u in users:
    print(f"id={u.id} email={u.email} role={u.role.name}")

db.close()