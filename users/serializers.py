from django.contrib.auth import get_user_model
from rest_framework import serializers

import keys
from helper.views import CommonHelper
from .models import UserData

User = get_user_model()


class UserDataSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()
    date_of_birth = serializers.DateField(format=keys.DATE_FORMAT)

    class Meta:
        model = UserData
        fields = [keys.ID, keys.NAME, keys.GENDER, keys.DATE_OF_BIRTH, keys.COMPANY_NAME, keys.CREATED]

    def get_created(self, instance):
        date = CommonHelper.convert_utc_to_local_timezone(instance.created)
        return date.strftime(keys.DATE_FORMAT +" "+keys.TIME_FORMAT)
