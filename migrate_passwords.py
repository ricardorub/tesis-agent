"""
Script para migrar contraseñas en texto plano a formato hash (pbkdf2:sha256).
Ejecutar UNA SOLA VEZ después de actualizar auth_controller.py.

Uso:
    python migrate_passwords.py
"""
from app import app
from model.db import db
from model.models import User
from werkzeug.security import generate_password_hash

def is_already_hashed(password: str) -> bool:
    """Detecta si la contraseña ya está hasheada por Werkzeug."""
    return password.startswith("pbkdf2:") or password.startswith("scrypt:")

def migrate():
    with app.app_context():
        users = User.query.all()
        migrated = 0
        skipped = 0

        for user in users:
            if is_already_hashed(user.password):
                print(f"  [SKIP] {user.email} — ya tiene hash")
                skipped += 1
            else:
                plain_password = user.password
                user.password = generate_password_hash(plain_password)
                print(f"  [OK]   {user.email} — contraseña hasheada")
                migrated += 1

        db.session.commit()
        print(f"\n✅ Migración completa: {migrated} hasheadas, {skipped} omitidas.")

if __name__ == "__main__":
    migrate()
