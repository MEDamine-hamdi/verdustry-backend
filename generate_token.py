from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.utils.jwt import create_access_token

db = SessionLocal()
repo = UserRepository(db)
user = repo.get_by_email("aminehamdi11223@gmail.com")

if user:
    token = create_access_token(data={"sub": str(user.id)})
    print("TOKEN:", token)
else:
    print("Utilisateur introuvable")

db.close()