import pytest
import bcrypt
from src.core.User import User

class TestUser:
    def test_user_init(self):
        username = "tUser"
        password = "tPWD123"
        email = "test@test.com"
        full_name = "Test Test"

        user = User(username = username, password = password, email = email, full_name = full_name)
        assert user.username == username
        assert user.email == email
        assert user.full_name == full_name
        assert user.role == "user"
        assert user.user_id is not None # making sure that uuid is generted

    def test_password_hashing(self):
        password = "secure_password"
        user = User(
            username="tUser",
            password = password,
            email="test@test.com",
            full_name="Test Test"
        )

        assert password != user.password
        assert user.password.startswith("$2b$")

        assert user.verify_password(user.password) is True

        assert user.verify_password("wrong pwd") is False

    def test_to_dict(self): # testing converion to dictionary
        user = User(
            username="tUser",
            password= "tPWD123",
            email="test@test.com",
            full_name="Test Test",
            user_id="test-uuid",
            created_at="2025-03-05T00:00:00"
        )

        user_dict = user.to_dict()
        assert user_dict["username"] == "tUser"
        assert user_dict["email"] == "test@test.com"
        assert user_dict["full_name"] == "Test Test"
        assert user_dict["user_id"] == "test-uuid"
        assert user_dict["role"] == "user"
        assert user_dict["created_at"] == "2025-03-05T00:00:00"

    def test_from_dict(self): # testing process of creating user by extracting info from dict
        user_data = {
            "username": "dictuser",
            "password": "$2b$12$hashed_pwd",  # password stored in hashed
            "email": "dict@example.com",
            "full_name": "Dict User",
            "role": "admin",
            "user_id": "dict-uuid",
            "created_at": "2025-01-02T00:00:00"
        }

        user  = User.from_dict(user_data)
        assert user.username == "dictuser"
        assert user.password == "$2b$12$hashed_pwd"
        assert user.email == "dict@example.com"
        assert user.full_name == "Dict User"
        assert user.role == "admin"
        assert user.user_id == "dict-uuid"
        assert user.created_at == "2025-01-02T00:00:00"