import pytest
from unittest.mock import patch, MagicMock
from src.managers.UserManager import UserManager
from src.core.User import User

class TestUserManager:
    @pytest.fixture
    def mock_users_data(self):
        """ sample user data for tests """
        return [
            {
                "user_id": "user-1",
                "username": "tUser1",
                "password": "$2b$12$hashed_password1",
                "email": "tuser1@example.com",
                "full_name": "Test Usero",
                "role": "user",
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "user_id": "user-2",
                "username": "tUser2",
                "password": "$2b$12$hashed_password2",
                "email": "tuser2@example.com",
                "full_name": "Test Usert",
                "role": "user",
                "created_at": "2025-01-02T00:00:00"
            },
            {
                "user_id": "admin-1",
                "username": "admin",
                "password": "$2b$12$hashed_admin_password",
                "email": "admin@example.com",
                "full_name": "Admin User",
                "role": "admin",
                "created_at": "2025-01-03T00:00:00"
            }
        ]

    @patch('src.utils.json_utils.load_json')
    def test_get_all_users(self, mock_load_json, mock_users_data):
        """ getting all users """
        mock_load_json.return_value = mock_users_data

        user_manager = UserManager()
        users = user_manager.get_all_users()

        assert len(users) == 3
        assert isinstance(users[0], User)
        assert users[0].user_id == "user-1"
        assert users[1].user_id == "user-2"
        assert users[2].user_id == "admin-1"

        mock_load_json.assert_called_once_with('users.json')

    @patch('src.utils.json_utils.load_json')
    def test_get_user_by_id(self, mock_load_json, mock_users_data):
        mock_load_json.return_value = mock_users_data

        user_manager = UserManager()
        user = user_manager.get_user_by_id("user-2")

        assert user is not None
        assert user.user_id == "user-2"
        assert user.username == "tUser2"
        assert user.email == "tuser2@example.com"
        assert user.role == "user"

    @patch('src.utils.json_utils.load_json')
    def test_get_user_by_id_not_found(self, mock_load_json, mock_users_data):
        mock_load_json.return_value = mock_users_data

        user_manager = UserManager()
        user = user_manager.get_user_by_id("dne-id")

        assert user is None

    @patch('src.utils.json_utils.load_json')
    def test_get_user_by_username(self, mock_load_json, mock_users_data):
        mock_load_json.return_value = mock_users_data

        user_manager = UserManager()
        user = user_manager.get_user_by_username("admin")

        assert user is not None
        assert user.username == "admin"
        assert user.user_id == "admin-1"
        assert user.role == "admin"

    @patch('src.utils.json_utils.load_json')
    def test_get_user_by_username_not_found(self, mock_load_json, mock_users_data):
        mock_load_json.return_value = mock_users_data

        user_manager = UserManager()
        user = user_manager.get_user_by_username("dne-username")

        assert user is None

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_create_user(self, mock_save_json, mock_load_json, mock_users_data):
        mock_load_json.return_value = mock_users_data
        mock_save_json.return_value = True

        user_manager = UserManager()

        user_data = {
            "username": "newuser",
            "password": "password123",
            "email": "newuser@example.com",
            "full_name": "New User"
        }

        user_id = user_manager.create_user(user_data)

        assert user_id is not None
        mock_save_json.assert_called_once()

        # Check the saved data
        saved_data = mock_save_json.call_args[0][1]
        assert len(saved_data) == 4  # Original 3 + new one
        assert saved_data[3]["username"] == "newuser"
        assert saved_data[3]["email"] == "newuser@example.com"
        assert saved_data[3]["full_name"] == "New User"
        assert saved_data[3]["role"] == "user"  # default setting

        # Password should be hashed
        assert saved_data[3]["password"].startswith("$2b$")
        assert saved_data[3]["password"] != "password123"

    @patch('src.utils.json_utils.load_json')
    def test_create_user_duplicate_username(self, mock_load_json, mock_users_data):
        mock_load_json.return_value = mock_users_data

        user_manager = UserManager()

        user_data = {
            "username": "tUser1",  # alr exists
            "password": "password123",
            "email": "another@example.com",
            "full_name": "Another User"
        }

        with pytest.raises(ValueError) as excinfo:
            user_manager.create_user(user_data)

        assert "username 'tUser1' already exists" in str(excinfo.value)

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_update_user(self, mock_save_json, mock_load_json, mock_users_data):
        mock_load_json.return_value = mock_users_data
        mock_save_json.return_value = True

        user_manager = UserManager()

        update_data = {
            "email": "updated@example.com",
            "full_name": "Updated Name"
        }

        result = user_manager.update_user("user-1", update_data)

        assert result is True
        mock_save_json.assert_called_once()

        # Check the saved data
        saved_data = mock_save_json.call_args[0][1]
        updated_user = next((u for u in saved_data if u["user_id"] == "user-1"), None)
        assert updated_user["email"] == "updated@example.com"
        assert updated_user["full_name"] == "Updated Name"
        assert updated_user["username"] == "tUser1"

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_update_user_password(self, mock_save_json, mock_load_json, mock_users_data):
        mock_load_json.return_value = mock_users_data
        mock_save_json.return_value = True

        user_manager = UserManager()

        update_data = {
            "password": "new_pwd123"
        }

        result = user_manager.update_user("user-1", update_data)

        assert result is True
        mock_save_json.assert_called_once()

        saved_data = mock_save_json.call_args[0][1]
        updated_user = next((u for u in saved_data if u["user_id"] == "user-1"), None)

        # making sure pwd is still hashed
        assert updated_user["password"].startswith("$2b$")
        assert updated_user["password"] != "new_pwd123"
        assert updated_user["password"] != "$2b$12$hashed_password1"

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_update_user_not_found(self, mock_save_json, mock_load_json, mock_users_data):
        """ updating a dne user """
        mock_load_json.return_value = mock_users_data

        user_manager = UserManager()

        update_data = { "email": "updated@example.com"}

        result = user_manager.update_user("dne-id", update_data)

        assert result is False
        mock_save_json.assert_not_called()

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_delete_user(self, mock_save_json, mock_load_json, mock_users_data):
        mock_load_json.return_value = mock_users_data
        mock_save_json.return_value = True

        user_manager = UserManager()

        result = user_manager.delete_user("user-2")

        assert result is True
        mock_save_json.assert_called_once()

        saved_data = mock_save_json.call_args[0][1]
        assert len(saved_data) == 2  # 3-1 = 2

        # user-2 should be GONE!
        user_ids = [u["user_id"] for u in saved_data]
        assert "user-2" not in user_ids
        assert "user-1" in user_ids
        assert "admin-1" in user_ids

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_delete_user_not_found(self, mock_save_json, mock_load_json, mock_users_data):
        mock_load_json.return_value = mock_users_data

        user_manager = UserManager()

        result = user_manager.delete_user("dne-id")

        assert result is False
        mock_save_json.assert_not_called()

    @patch('src.utils.json_utils.load_json')
    def test_authenticate_user_success(self, mock_load_json, mock_users_data):
        mock_load_json.return_value = mock_users_data

        user = User.from_dict(mock_users_data[0])
        user.verify_password = MagicMock(return_value=True)

        UserManager.get_user_by_username = MagicMock(return_value=user)

        user_manager = UserManager()
        authenticated_user = user_manager.authenticate_user("tUser1", "password123")

        assert authenticated_user is not None
        assert authenticated_user.user_id == "user-1"
        user.verify_password.assert_called_once_with("password123")

    @patch('src.utils.json_utils.load_json')
    def test_authenticate_user_wrong_password(self, mock_load_json, mock_users_data):
        """ auth process with wrong pwd """
        mock_load_json.return_value = mock_users_data

        user = User.from_dict(mock_users_data[0])
        user.verify_password = MagicMock(return_value=False)

        UserManager.get_user_by_username = MagicMock(return_value=user)

        user_manager = UserManager()
        authenticated_user = user_manager.authenticate_user("tUser1", "wrong_password")

        assert authenticated_user is None
        user.verify_password.assert_called_once_with("wrong_password")

    @patch('src.utils.json_utils.load_json')
    def test_authenticate_user_not_found(self, mock_load_json, mock_users_data):
        """ auth with nonexisting username"""
        mock_load_json.return_value = mock_users_data

        UserManager.get_user_by_username = MagicMock(return_value=None)

        user_manager = UserManager()
        authenticated_user = user_manager.authenticate_user("non_existent", "password123")

        assert authenticated_user is None