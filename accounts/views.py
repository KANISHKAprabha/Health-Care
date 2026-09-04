from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accounts.serializers import LoginSerializer, RegisterSerializer
from accounts.services import AuthService
from api.responses import success_response


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = AuthService.register(**serializer.validated_data)
        return success_response(tokens, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = AuthService.login(**serializer.validated_data)
        return success_response(tokens)
