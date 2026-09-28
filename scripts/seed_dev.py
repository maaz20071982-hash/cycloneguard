#!/usr/bin/env python3
"""
=============================================================================
CYCLONEGUARD — DEVELOPMENT DATABASE SEEDING SCRIPT
=============================================================================
WARNING: THIS SCRIPT IS FOR LOCAL DEVELOPMENT ONLY.
DO NOT EXECUTE IN PRODUCTION.

This script creates ONE development administrator account using credentials
read dynamically from environment variables. No password is hard-coded.
"""

import sys
import os

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository


def seed_development_admin():
    print("------------------------------------------------------------")
    print("CYCLONEGUARD DEVELOPMENT DATABASE SEEDER (DEVELOPMENT ONLY)")
    print("------------------------------------------------------------")

    if settings.ENVIRONMENT.lower() == "production":
        print("ERROR: Seeder script cannot run in production environment!")
        sys.exit(1)

    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        admin_email = settings.DEV_ADMIN_EMAIL.lower().strip()
        admin_name = settings.DEV_ADMIN_NAME
        admin_password = settings.DEV_ADMIN_PASSWORD

        if not admin_password:
            print("ERROR: DEV_ADMIN_PASSWORD environment variable is empty.")
            sys.exit(1)

        existing_user = user_repo.get_by_email(admin_email)
        if existing_user:
            print(f"[!] Dev Admin already exists: {existing_user.email} (Role: {existing_user.role})")
            return

        print(f"Creating ONE development admin account:")
        print(f"  Name:  {admin_name}")
        print(f"  Email: {admin_email}")
        print(f"  Role:  {UserRole.ADMIN}")

        hashed_password = hash_password(admin_password)

        new_admin = user_repo.create_user(
            name=admin_name,
            email=admin_email,
            password_hash=hashed_password,
            role=UserRole.ADMIN,
            is_active=True,
        )

        print(f"[+] Successfully seeded development admin user: {new_admin.id}")
        print("Note: In production, initial admin accounts must be created through secure CLI provisioning.")

    except Exception as e:
        print(f"[-] Error seeding development database: {e}")
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_development_admin()
