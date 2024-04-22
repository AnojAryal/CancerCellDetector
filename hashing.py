from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class Hashing:
    def bycript(password: str):
        hashed_password = pwd_context.hash(password)
        return hashed_password

        def verify(hashed_password, plain_password):
            return pwd_context.verify(plain_password, hashed_password)