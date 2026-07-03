# src/app/utils/hashing.py

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Converts plain text password to bcrypt hash"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if plain password matches stored hash.
    Used during login.
    Django comparison: similar to check_password() on User model
    """
    return pwd_context.verify(plain_password, hashed_password)