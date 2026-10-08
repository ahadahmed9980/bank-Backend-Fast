from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_Password(password: str) -> str:
    return password_hash.hash(password)


def compare_password(plain_password: str, hased_password: str) -> bool:
    return password_hash.verify(plain_password, hash_Password)
