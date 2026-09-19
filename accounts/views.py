from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from salon.models import Stylist

from .exceptions import FailedSendMassageError, FailedSendOTPError
from .serializers import OTPVerifySerializer, RegisterOrLoginSerializer, ProfileSerializer
from .services.otp_service import OTPService
from .services.sms_service import SmsService
from .throttles import LoginThrottle

User = get_user_model()


class RegisterOrLoginView(APIView):
    permission_classes = [permissions.AllowAny]  # noqa: RUF012
    throttle_classes = [LoginThrottle]

    def post(self, request):

        serializer = RegisterOrLoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        code = OTPService.generate_otp(phone_number)

        try:
            SmsService.send_otp(phone_number, code)
        except FailedSendOTPError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
        )

        if created:
            unlinked_stylist = Stylist.objects.filter(
                phone=phone_number, user__isnull=True
            ).first()

            if unlinked_stylist:
                user.role = User.Role.STYLIST
                unlinked_stylist.user = user
                unlinked_stylist.save(update_fields=["user"])
                user.save(update_fields=["role"])



        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": (
                    "registered successfully" if created else "logged in successfully"
                ),
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "is_new_user": created,
                "phone_number": phone_number,
                "first_name" : user.profile.first_name,
                "last_name" : user.profile.last_name,
            },
            status=status.HTTP_200_OK,
        )


class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, many=False)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        profile = user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()


        return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)

