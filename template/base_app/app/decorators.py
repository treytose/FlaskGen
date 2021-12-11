from flask_login import current_user

def permission_required(*permissions):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.can(*permissions):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator