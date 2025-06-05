from flask_jwt_extended import create_access_token, get_jwt_identity
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request

def generate_token(user_id, username, role):
    info = {'user_id': user_id,'username': username,'role': role}
    return create_access_token(identity=info)

def admin_required(fn): # decorator to require admin role for a route | fn -- function to decorate | returns decorated func
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        if identity.get('role') != 'admin': return jsonify(message="admin access required"), 403
        return fn(*args, **kwargs)
    return wrapper

def get_current_user(): return get_jwt_identity()