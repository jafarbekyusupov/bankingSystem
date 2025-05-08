import pytest
from unittest.mock import patch
from src.managers.UserManager import UserManager

class TestUserManager:
    @pytest.fixture #(autouse=True)
    def mock_data(self):
        ''' sample user data '''
        return [
            {
                "user_id" : "user-1",
                "username" : "tUser-1",
                "password" : "$2b$12$hashed_pwd1",
                "full_name" : "T Test1",
                "role" : "user",
                "created_at" : "2025-01-01T00:00:00",
            },
            {
                "user_id": "user-2",
                "username": "tUser-2",
                "password": "$2b$12$hashed_pwd2",
                "full_name": "T Test2",
                "role": "admin",
                "created_at": "2025-02-02T00:00:00",
            }
        ]

    @patch('src.utils.json_utils.load_json')
    def test_get_all_users(self, mock_load_json, mock_data):
        ''' test getting all users'''
        mock_load_json.return_value = mock_data

        manager = UserManager()
        users = manager.get_all_users()

        assert len(users) == 2
        assert users[0]['user_id'] == 'user-1'
        assert users[1]['user_id'] == 'user-2'

    @patch('src.utils.json_utils.load_json')
    def test_get_user_by_id(self, mock_load_json, mock_data):
        ''' test getting users by id '''
        mock_load_json.return_value = mock_data

        manager = UserManager()
        user = manager.get_user_by_id('user-2')

        assert user is not None
        assert user.username == 'tUser-2'
        assert user.role == 'admin'

    @patch('src.utils.json_utils.load_json')
    def test_get_user_by_id_not_found(self, mock_load_json, mock_data): # gubid - get User by ID
        ''' test cases when we tryna access non-existsent user by id '''
        mock_load_json.return_value = mock_data

        manager = UserManager()
        user = manager.get_user_by_id('user-doesnt-exist')

        assert user is None

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_create_user(self, mock_save_json, mock_load_json, mock_data):
        ''' test creating a new user '''
        mock_load_json.return_value = mock_data
        mock_save_json.return_value = True

        user_manager = UserManager()

        nUserData = {
            "username": "nUser",
            "password": "$2b$12$hashed_pwd0",
            "email": "nuser@example.com",
            "full_name": "New User",
        }

        user_id = user_manager.create_user(nUserData)

        assert user_id is not None
        mock_save_json.assert_called_once()

        # checking data that should be saved

        saved_data = mock_save_json.call_args[0][1]
        assert len(saved_data) == 3
        assert saved_data[2]['username'] == 'nUser'
        assert saved_data[2]['password'] == '$2b$12$hashed_pwd0'
        assert saved_data[2]['email'] == 'nuser@example.com'


    @patch('src.utils.json_utils.load_json')
    def test_create_user_with_duplicate_username(self, mock_load_json, mock_data):
        ''' test creating a new user with duplicate username, should raise a valueError '''
        mock_load_json.return_value = mock_data

        user_manager = UserManager()

        dup_userData = {
            "username": "nUser", # this alr exists
            "password": "$2b$12$hashed_pwd1",
            "email" : "dup@exmaple.com",
            "full_name" : "Dup User"
        }

        with pytest.raises(ValueError):
            user_manager.create_user(dup_userData)