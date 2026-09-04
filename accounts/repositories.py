from accounts.models import User


class UserRepository:
    @staticmethod
    def get_by_email(email):
        return User.objects.filter(email=email).first()

    @staticmethod
    def create(email, name, password):
        return User.objects.create_user(email=email, name=name, password=password)
