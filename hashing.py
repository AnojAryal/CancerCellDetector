from passlib.context import CryptContext

# Creating a CryptContext instance with bcrypt hashing scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# hashing password
class Hashing:
    def bcrypt(password: str):
        hashed_password = pwd_context.hash(password)
        return hashed_password

    def verify(hashed_password, plain_password):
        return pwd_context.verify(plain_password, hashed_password)
