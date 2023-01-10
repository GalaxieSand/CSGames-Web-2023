from Models.User import User
from flask import jsonify


class UserService:
    def __init__(self, user_store):
        self.userStore = user_store

    def user_login(self, client, username, password):
        password_hash = User.HashPassword(password)

        user = self.userStore.get_user_with_login(username, password_hash, client.id)

        return user

    def create_user_without_client(self, username, password):
        user = User.NewUser(username, password, None)

        user.claims = {
            "role": "user"
        }

        subject = self.userStore.add_user_without_client(user)

        if subject is None:
            return "User Already Exists", 400
        else:
            return jsonify({
                "sub": subject
            }), 201

        return user

    def create_user(self, client, username, password):

        user = User.NewUser(username, password, client.id)

        user.claims = {
            "role": "user"
        }

        subject = self.userStore.add_user(user)

        if subject is None:
            return "User Already Exists", 400
        else:
            return jsonify({
                "sub": subject
            }), 201

        return user