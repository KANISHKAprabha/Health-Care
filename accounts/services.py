from rest_framework_simplejwt.tokens import RefreshToken

from accounts.repositories import UserRepository
from api.exceptions import InvalidCredentialsError


def _tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}



class AuthService:
    @staticmethod
    def register(email, name, password):
        # No pre-insert duplicate-email check here: email is unique at the DB
        # level, and that constraint is the accepted defense for this rare,
        # one-shot action (see ARCHITECTURE.MD §9).
        user = UserRepository.create(email=email, name=name, password=password)
        return _tokens_for(user)

    @staticmethod
    def login(email, password):
        user = UserRepository.get_by_email(email)
        if user is None or not user.check_password(password):
            raise InvalidCredentialsError()
        return _tokens_for(user)
