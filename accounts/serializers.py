from rest_framework import serializers
from .utils import normalize_phone_number


class RegisterOrLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=20)

    def validate_phone_number(self, value):

        try:
            normalized = normalize_phone_number(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

        return normalized


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=20)
    code = serializers.CharField(required=True, min_length=5, max_length=6)

    def validate_phone_number(self, value):
        try:
            normalized = normalize_phone_number(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        return normalized

    def validate_code(self, value):
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("کد باید فقط شامل عدد باشد.")
        return value
