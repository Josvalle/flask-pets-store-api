import jwt
from functools import wraps
from flask import jsonify,request,Response

class JWT_Manager:
    def __init__(self):
        with open('private_key.pem', 'rb') as private:
            self.private_key = private.read()
        with open('public_key.pem', 'rb') as public:
            self.public_key = public.read()

    
    def encode(self, data):
        try:
            encoded = jwt.encode(data, self.private_key, algorithm="RS256")
            return encoded
        except Exception as e:
            print(f"Error: {e}")
            return None

    def decode(self, token):
        try:
            decoded = jwt.decode(token, self.public_key, algorithms=["RS256"])
            return decoded
        except Exception as e:
            print(e)
            return None
    

jwt_manager = JWT_Manager ()
def admin_only(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        token = request.headers.get('Authorization')
        if(token is not None):
            token = token.replace("Bearer ","")
            decoded = jwt_manager.decode(token)
            role_value = decoded['role']
            if role_value != 'admin':
                return jsonify({"error":'You are not allow to perform this action '}), 403
            return func(*args, **kwargs)
        else:
            return Response(status=403)
    return wrapper