from src.core.User import User
from src.utils.json_utils import load_json, save_json


class UserManager:
    """ manager class for handling user operations """

    def __init__(self):
        self.users_file = 'users.json'

    def get_all_users(self):
        """ returns -- list of user objects """
        users_data = load_json(self.users_file)
        return [User.from_dict(user_data) for user_data in users_data]

    def get_user_by_id(self, user_id):
        """
        get a user by id

        args: user_id (str) -- user id

        returns: user -- user obj if found else none
        """
        users = self.get_all_users()
        for user in users:
            if user.user_id == user_id:
                return user
        return None

    def get_user_by_username(self, username):
        """
        get a user by username

        args: username (str) -- username

        returns: user -- user obj if found else none
        """
        users = self.get_all_users()
        for user in users:
            if user.username == username:
                return user
        return None

    def create_user(self, user_data):
        """
        create a new user

        args: user_data (dict) -- user data dict

        returns: str -- user id if successful else none

        raises: ValueError - if username alr exists
        """
        # check if username alr exists
        if self.get_user_by_username(user_data['username']):
            raise ValueError(f"username '{user_data['username']}' already exists")

        # new user
        user = User(
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email'],
            full_name=user_data['full_name'],
            role=user_data.get('role', 'user')
        )

        # save user
        users_data = load_json(self.users_file)
        users_data.append(user.to_dict())

        if save_json(self.users_file, users_data):
            return user.user_id
        return None

    def update_user(self, user_id, user_data):
        """
        upd an existing user

        args:
            user_id (str): user id
            user_data (dict): updated user data

        returns: bool -- true if successful else false
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        # update user fields
        for key, value in user_data.items():
            if key == 'password' and value and not value.startswith('$2b$'):
                # hash new password
                value = user._hash_password(value)

            if hasattr(user, key) and key != 'user_id':
                setattr(user, key, value)

        # save updated user
        users_data = load_json(self.users_file)

        # find and replace user in list
        for i, u in enumerate(users_data):
            if u['user_id'] == user_id:
                users_data[i] = user.to_dict()
                break

        return save_json(self.users_file, users_data)

    def delete_user(self, user_id):
        """
        delete a user

        args: user_id (str) -- user id

        returns: bool -- true if successful else false
        """
        users_data = load_json(self.users_file)

        # find and remove user
        for i, user in enumerate(users_data):
            if user['user_id'] == user_id:
                del users_data[i]
                return save_json(self.users_file, users_data)

        return False

    def authenticate_user(self, username, password):
        """
        auth user

        args:
            username (str): username
            password (str): password

        returns: user -- user obj if found else none
        """
        user = self.get_user_by_username(username)
        if user and user.verify_password(password): return user

        return None