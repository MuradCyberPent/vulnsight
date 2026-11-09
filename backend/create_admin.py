"""Make an existing user an admin:   python create_admin.py <username>"""
import sys

from sqlalchemy import func

from app.core.database import SessionLocal
from app.core.models import User

if len(sys.argv) != 2:
    sys.exit("Usage: python create_admin.py <username>")

db = SessionLocal()
user = db.query(User).filter(func.lower(User.username) == sys.argv[1].lower()).first()
if not user:
    sys.exit(f"No user named '{sys.argv[1]}'. Register that account first.")
user.role = "admin"
db.commit()
print(f"{user.username} is now an admin.")
