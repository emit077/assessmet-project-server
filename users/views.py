from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import keys
import messages
from helper.views import HelperAuthentication
from users.models import UserData
from users.serializers import UserDataSerializer

Users = get_user_model()


@api_view(['POST'])
# @renderer_classes([SwaggerUIRenderer, OpenAPIRenderer])
def login(request):
    """
        mobile -- mobile number is required
        password -- password is required
    """
    mobile = request.data.get(keys.MOBILE, None)
    password = request.data.get(keys.PASSWORD, None)

    if not Users.objects.filter(mobile=mobile).exists():
        return Response({
            keys.SUCCESS: False,
            keys.MESSAGE: messages.MOBILE_NUMBER_NOT_REGISTER
        }, status=status.HTTP_200_OK)

    try:
        user = Users.objects.get(mobile=mobile)
    except ObjectDoesNotExist:
        return Response({
            keys.SUCCESS: False,
            keys.MESSAGE: messages.MOBILE_NUMBER_NOT_REGISTER
        }, status=status.HTTP_200_OK)

    print(check_password(password, user.password))
    print(authenticate(mobile=mobile, password=password))
    if not check_password(password, user.password):
        return Response({
            keys.SUCCESS: False,
            keys.MESSAGE: messages.INVALID_CREDENTIALS
        }, status=status.HTTP_200_OK)

    else:
        response = {
            keys.SUCCESS: True,
            keys.MESSAGE: messages.SUCCESS
        }
        headers = {
            keys.ACCESS_TOKEN: HelperAuthentication.get_token(user)
        }

        return Response(response, status=status.HTTP_200_OK, headers=headers)


@api_view(['POST'])
def resend_otp(request):
    otp_token = request.headers[keys.OTP_TOKEN]
    try:
        user = Users.objects.get(otp_token=otp_token)
        was_limited = getattr(request, 'limited', False)
        if not was_limited:
            HelperAuthentication.send_otp(user.otp_token, str(user.mobile))
        else:
            return Response({
                keys.SUCCESS: False,
                keys.MESSAGE: messages.USER_RESEND_OTP_LIMIT_REACHED
            }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({
            keys.SUCCESS: False,
            keys.MESSAGE: messages.USER_INVALID_OTP_TOKEN
        }, status=status.HTTP_403_FORBIDDEN)
    return Response({
        keys.SUCCESS: True,
        keys.MESSAGE: messages.SUCCESS
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def verify_otp(request):
    """
    verify otp api ¬
    """
    otp_token = request.headers[keys.OTP_TOKEN]
    otp = request.POST.get(keys.OTP)
    try:
        user = Users.objects.get(otp_token=otp_token)
        if not HelperAuthentication.verify_otp(otp, otp_token):
            return Response({
                keys.SUCCESS: False,
                keys.MESSAGE: messages.INVALID_OTP
            }, status=status.HTTP_200_OK)
        else:
            user.is_otp_verified = True
            user.save()
    except ObjectDoesNotExist:
        return Response({
            keys.SUCCESS: False,
            keys.MESSAGE: messages.USER_INVALID_OTP_TOKEN
        }, status=status.HTTP_403_FORBIDDEN)

    response = {
        keys.SUCCESS: True,
        keys.MESSAGE: messages.SUCCESS
    }
    headers = {
        keys.ACCESS_TOKEN: HelperAuthentication.get_token(user)
    }
    return Response(response, status=status.HTTP_200_OK, headers=headers)


@api_view(['POST'])
def forget_password(request):
    """
    forget password api
    """
    mobile = request.POST.get(keys.MOBILE)

    try:
        user = Users.objects.get(mobile=mobile)
        user.otp_token = HelperAuthentication.generate_otp_token()
        user.save()
        otp = HelperAuthentication.send_otp(user.otp_token, user.mobile)
    except ObjectDoesNotExist:
        return Response({
            keys.SUCCESS: False,
            keys.MESSAGE: messages.USER_NOT_FOUND
        }, status=status.HTTP_200_OK)

    headers = {
        keys.OTP_TOKEN: user.otp_token,

    }
    response = {
        keys.SUCCESS: True,
        keys.MESSAGE: messages.SUCCESS,
        keys.OTP: otp
    }

    return Response(response, status=status.HTTP_200_OK, headers=headers)


@api_view(['POST'])
def reset_password(request):
    response = {
        keys.SUCCESS: True,
        keys.MESSAGE: messages.SUCCESS
    }
    password = request.POST.get(keys.PASSWORD)

    try:
        user = HelperAuthentication.get_users_instance(request)
        print(user.mobile)
        user.set_password(password)
        user.save()
        response[keys.MESSAGE] = messages.SUCCESS
    except ObjectDoesNotExist:
        response[keys.SUCCESS] = False
        response[keys.MESSAGE] = messages.USER_NOT_FOUND

    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
# @CustomDjangoDecorators.validate_access_token
def add_user(request):
    print(request.data)
    id = request.data.get(keys.ID, None)
    name = request.data.get(keys.NAME, None)
    company_name = request.data.get(keys.COMPANY_NAME, None)
    gender = request.data.get(keys.GENDER, None)
    date_of_birth = request.data.get(keys.DATE_OF_BIRTH, None)

    try:
        user = UserData.objects.get(id=id)
    except ObjectDoesNotExist:
        user = UserData()

    user.name = name
    user.company_name = company_name
    user.gender = gender
    user.date_of_birth = date_of_birth
    user.save()

    response = {
        keys.SUCCESS: True,
        keys.MESSAGE: keys.SUCCESS
    }
    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
# @CustomDjangoDecorators.validate_access_token
def get_user_list(request):
    user = HelperAuthentication.get_users_instance(request)

    search_query = request.GET.get(keys.SEARCH_QUERY, None)
    sort_by = request.GET.get(keys.SORT_BY, None)
    page_number = request.GET.get(keys.PAGE_NUMBER, 1)
    page_length = request.GET.get(keys.PAGE_LENGTH, 20)

    queryset = UserData.objects.filter(user=None)

    if sort_by is not None and sort_by != "":
        queryset = UserData.objects.filter().order_by(sort_by)

    if search_query:
        queryset = queryset.filter(Q(name__icontains=search_query) | Q(company_name__icontains=search_query))

    paginator = Paginator(queryset, page_length)
    try:
        queryset = paginator.page(page_number)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    user_list = UserDataSerializer(queryset, many=True)

    response = {
        keys.SUCCESS: True,
        keys.MESSAGE: messages.SUCCESS,
        keys.TOTAL_PAGE_COUNT: paginator.num_pages,
        keys.USER_LIST: user_list.data,
    }

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
# @CustomDjangoDecorators.validate_access_token
def get_details(request):
    id = request.GET.get(keys.ID, None)
    try:
        user = UserData.objects.get(id=id)
    except ObjectDoesNotExist:
        return Response({keys.SUCCESS: False, keys.MESSAGE: messages.USER_NOT_FOUND}, status=status.HTTP_200_OK)

    response = {
        keys.SUCCESS: True,
        keys.MESSAGE: messages.SUCCESS,
        keys.NAME: user.name,
        keys.GENDER: user.gender,
        keys.DATE_OF_BIRTH: user.date_of_birth,
        keys.COMPANY_NAME: user.company_name,
    }

    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
# @CustomDjangoDecorators.validate_access_token
def delete_user(request):
    id = request.data.get(keys.ID, None)
    try:
        user = UserData.objects.get(id=id).delete()
    except ObjectDoesNotExist:
        return Response({keys.SUCCESS: False, keys.MESSAGE: messages.USER_NOT_FOUND}, status=status.HTTP_200_OK)

    response = {
        keys.SUCCESS: True,
        keys.MESSAGE: messages.SUCCESS,
    }

    return Response(response, status=status.HTTP_200_OK)
