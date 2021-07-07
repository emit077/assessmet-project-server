# Create your views here.
from functools import wraps

import pytz
from pyotp import random_base32, TOTP
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

import keys
import messages
from Assessment_2112_server.settings import TIME_ZONE


class HelperAuthentication:
    @staticmethod
    def get_token(user):
        """
        Method used to obtain a new token
        :param request: user instance
        :return:
        """
        print("get Token")
        try:
            token = Token.objects.get(user=user)
        except:
            return None
        return token.key

    @staticmethod
    def refresh_token(user):
        """
        Method used to refresh token
        :param : user instance
        :return:
        """
        try:
            token = Token.objects.get(user=user)
            token.delete()
            Token.objects.create(user=user)
        except:
            Token.objects.create(user=user)

        return token.key

    @staticmethod
    def verify_token(request):
        """
        Method used to verify the token
        :return:
        """
        print("request==")
        print(request.headers)
        try:
            token = request.headers[keys.ACCESS_TOKEN]
            if Token.objects.filter(key=token).exists():
                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def get_users_instance(request):
        """
        Method used to verify the token
        :return:
        """
        try:
            token = request.headers[keys.ACCESS_TOKEN]
            instance = Token.objects.get(key=token)
            return instance.user
        except:
            return None

    @staticmethod
    def generate_otp_token():
        """
        Generates a random OTP token to use later for verification.
        :return: random base32 OTP token
        """
        return random_base32()

    @staticmethod
    def send_otp(secret, mobile):
        otp = TOTP(secret, digits=keys.OTP_LENGTH).now()
        # sms = messages.OTP_FORMAT.format(otp=otp)
        # send_sms(mobile, sms)
        return otp

    @staticmethod
    def verify_otp(otp, secret):
        return TOTP(secret, digits=keys.OTP_LENGTH).verify(otp, valid_window=4)


class CustomDjangoDecorators:
    """
    Define all the custom decorators here.
    """

    @staticmethod
    def validate_access_token(function):
        """
        Custom decorator to verify user access token
        """

        @wraps(function)
        def wrap(request, *args, **kwargs):
            res = HelperAuthentication.verify_token(request)
            if not res:
                return Response(data={keys.SUCCESS: False, keys.MESSAGE: messages.INVALID_TOKEN},
                                status=status.HTTP_403_FORBIDDEN)
            return function(request, *args, **kwargs)

        return wrap


class CommonHelper:

    @staticmethod
    def convert_utc_to_local_timezone(datetime_instance):
        """
        Used to convert UTC timezone to local timezone defined in settings
        :param datetime_instance:
        :return:
        """
        return datetime_instance.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIME_ZONE))
