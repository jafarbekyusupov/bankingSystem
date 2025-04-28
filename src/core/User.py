import uuid
import bcrypt
from datetime import datetime


class User:
    """ user class represents bank customers & admins """

    def __init__(self, username, password, email, full_name, role='user', user_id=None, created_at=None):
        """
        init a User obj

        args:
            username (str): unique username
            password (str): user pwd // which will be encrypted -- hashed
            email (str): user email address
            full_name (str): users full name
            role (str): user role/status ('user' or 'admin')
            user_id (str, optional): unique identifier, default is None -- generates UUID
            created_at (str, optional): user creation timestamp, default is None (cur time)
        """
        self.user_id = user_id if user_id else str(uuid.uuid4())
        self.username = username
        self.email = email
        self.full_name = full_name
        self.role = role
        self.created_at = created_at if created_at else datetime.now().isoformat()

        # hash password if not alr hashed
        self.password = self._hash_password(password) if not password.startswith('$2b$') else password

    def _hash_password(self, password):
        """
        hash pwd using bcrypt

        args: password (str) -- txt pwd

        returns: str --- hashed pwd
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    def verify_password(self, password):
        """
        verify if provided pwd matches stored hash

        args: password (str) -- pwd to verify

        returns: bool -- true if password matches else false
        """
        password_bytes = password.encode('utf-8')
        hashed_bytes = self.password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    def to_dict(self):
        """
        convert User to dictionary -- aka HASHMAP -- for serialization

        returns: dict -- User data as dict
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """
        create User from dict

        args: data (dict) -- User data dictionary

        returns: User object
        """
        return cls(
            username=data['username'],
            password=data['password'],
            email=data['email'],
            full_name=data['full_name'],
            role=data.get('role', 'user'),
            user_id=data.get('user_id'),
            created_at=data.get('created_at')
        )