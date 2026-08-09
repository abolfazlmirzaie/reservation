from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import OTPVerifySerializer, RegisterOrLoginSerializer
from .services.otp_service import OTPService
from .throttles import LoginThrottle

User = get_user_model()


class RegisterOrLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):

        serializer = RegisterOrLoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        code = OTPService.generate_otp(phone_number)

        print(f"OTP for {phone_number}: {code}")

        return Response(
            {"message": "OTP sent successfully."}, status=status.HTTP_200_OK
        )


class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):

        serializer = OTPVerifySerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        code = serializer.validated_data["code"]

        is_valid, error = OTPService.verify_otp(phone_number, code)

        if not is_valid:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                "role": User.Role.CUSTOMER,
            },
        )

        OTPService.delete_otp(phone_number)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": (
                    "registered successfully" if created else "logged in successfully"
                ),
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "is_new_user": created,
            },
            status=status.HTTP_200_OK,
        )
