import bcrypt
from lib.app_lib import AppLib

class Auth(AppLib):
    def __init__(self):
        super().__init__("libauth.log")

    def create_user(self, user):
        if "password" in user:
            user["password"] = bcrypt.hashpw(user["password"].encode('utf-8'), bcrypt.gensalt())
        
        errno = self.db.insert("user", user)
        if errno != 0:
            raise Exception("User creation failed")
        return {"error": 0, "message": "user created", "data": {"userid": self.db.lastInsId} }

if __name__ == '__main__':
    auth = Auth()