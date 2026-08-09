from rest_framework import serializers



class RegisterOrLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)


class OTPVerifySerializer(serializers.Serializer):
    code = serializers.CharField(required=True, max_length=6)
    phone_number = serializers.CharField(required=True, max_length=11)