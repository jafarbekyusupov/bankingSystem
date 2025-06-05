from src.models import db, User

class UserManager:
    def get_all_users(self): return User.query.all()
    def get_user_by_id(self,user_id): return User.query.filter_by(user_id=user_id).first()
    def get_user_by_username(self, username): return User.query.filter_by(username=username).first()

    def create_user(self, user_data):
        try:
            # check if username already exists
            if self.get_user_by_username(user_data['username']): raise ValueError(f"username '{user_data['username']}' already exists")

            # create new user
            user = User(username=user_data['username'],password=user_data['password'],email=user_data['email'],full_name=user_data['full_name'],role=user_data.get('role', 'user'))
            db.session.add(user)
            db.session.commit()
            return user.user_id
        except ValueError: raise
        except Exception as e:
            db.session.rollback()
            return None

    def update_user(self, user_id, user_data):
        try:
            user = self.get_user_by_id(user_id)
            if not user: return False

            # update user fields
            for key, value in user_data.items():
                if key == 'password' and value and not value.startswith('$2b$'): value = user._hash_password(value) # hash new password
                if hasattr(user, key) and key != 'user_id': setattr(user, key, value)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

    def delete_user(self, user_id):
        try:
            user = self.get_user_by_id(user_id)
            if not user: return False
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

    def authenticate_user(self, username, password):
        user = self.get_user_by_username(username)
        if user and user.verify_password(password): return user
        return None