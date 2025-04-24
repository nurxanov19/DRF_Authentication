import datetime
import random
import string
import uuid

from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser, OneTimePasswordModel

from django.contrib.auth.password_validation import validate_password as django_validate_password
from methodism import METHODISM
from authapp import methods


class Main(METHODISM):
    file = methods
    token_key = 'Token'
    not_auth_methods = ['register', 'login']



def validate_phone(phone):
    return False if len(str(phone)) != 12 or not isinstance(phone, int) or str(phone)[:3] != '998' else True

def validate_password(password: str):
    return False if len(password) < 6 or ' ' in password or not password.isalnum()  else True


class RegisterApiView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
        if 'key' not in data or 'password' not in data:
            return Response({
                'message': 'Password or name must be entered',
                'status': status.HTTP_401_UNAUTHORIZED
            })

        '''Kelayotgan data da key bo'lishi kerak'''

        # if len(str(data['phone'])) != 12 or not isinstance(data['phone'], int) or str(data['phone'])[:3] != '998':
        #     return Response({
        #         "Error": 'Telefon raqam xato kiritildi',
        #         'status': status.HTTP_400_BAD_REQUEST
        #     })

        if len(data['password']) < 6 or ' ' in data['password'] or not data['password'].isalnum() \
                or not any(x.isupper() for x in data['password']):  # any(map(lambda x: x.isupper(), data['password']))
            return Response({
                'Error': 'Password invalid',
                'status': status.HTTP_400_BAD_REQUEST
            })

        otp = OneTimePasswordModel.objects.filter(key=data.get('key')).first()
        phone = CustomUser.objects.filter(phone=otp.phone).first()
        if phone:
            return Response({
                'message': 'This user already exist',
                'status': status.HTTP_409_CONFLICT
            })

        user_data = {
            'phone': otp.phone,
            'password': data['password'],
            'name': data.get('name', '')
        }

        if data.get('key' ,'') == 'magic':      # key uchun alohida model yaratib qo'yish
            user_data.update({
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            })


        user = CustomUser.objects.create_user(**user_data)

        print("User created:", user.pk, user.phone)
        if user.pk is None:
            return Response({'message': 'User not saved successfully'}, status=500)

        token = Token.objects.create(user=user)
        print(token.key)
        return Response({
            'message': True,
            'Token': user.auth_token.key,
            'Status': status.HTTP_201_CREATED
        })


class LoginApiView(APIView):
    def post(self, request):
        data = request.data
        user = CustomUser.objects.filter(phone=data['phone']).first()

        if not user:
            return Response({
                'Error': 'Bu raqam orqali royxatdan otilmagan',
                'Status': status.HTTP_401_UNAUTHORIZED
            })

        if not user.check_password(data['password']):
            return Response({
                'Message': 'Parol xato kiritildi',
                'Status': status.HTTP_400_BAD_REQUEST
            })

        token = Token.objects.get_or_create(user=user)

        return Response({
            'Message': 'Success!',
            'Token': token[0].key,
            'Status': status.HTTP_200_OK
        })


# class LoginApiView(APIView):
#     def post(self, request):
#         data = request.data
#                             # authenticate() --> vazifasi biz kiritgan malumotlarni bazada bor yoki yo'qligini tekshiradi
#         if not authenticate(request, phone=data['phone'], password=data['password']):
#             return Response({
#                 'Error': 'Authenticate error',
#                 'Status': status.HTTP_400_BAD_REQUEST
#             })
#
#         user = CustomUser.objects.filter(phone=data['phone']).first()
#         token = Token.objects.get_or_create(user=user)
#
#         return Response({
#             'Message': 'Success!!!',
#             'Token': token[0].key,
#             'Status': status.HTTP_200_OK
#         })


class LogoutApiView(APIView):
    permission_classes = IsAuthenticated,
    authentication_classes = TokenAuthentication,

    def post(self, request):
        token = Token.objects.filter(user=request.user).first()
        token.delete()
        return Response({
            'Message': 'Logout Success!!',
            'Status': status.HTTP_200_OK
        })


class ProfileApiView(APIView):
    permission_classes = [IsAuthenticated]  # doim listda bergan afzal chunki,
    authentication_classes = [TokenAuthentication]   # drf list kutadi
    def get(self, request):
        user = request.user
        return Response({'data': user.format()})        # dict data ni postmanga yuborish ususli

    def patch(self, request):
        data = request.data

        if not validate_phone(data.get('phone', '')):
            return Response({
                "Error": 'Telefon raqam xato kiritildi',
                'status': status.HTTP_400_BAD_REQUEST
            })

        user = request.user
        if data['phone']:
            user_ = CustomUser.objects.filter(phone=data['phone']).first()

            if user.phone == data['phone']:
                return Response({
                    'Message': 'Bu sizning tel raqamingiz',
                    'Status': status.HTTP_400_BAD_REQUEST
                })

            if user_ and user_ != user:
                return Response({
                    'Message': 'Bu telefon mavjud',
                    'Status': status.HTTP_400_BAD_REQUEST
                })

        user.name = data.get("name", user.name)
        user.phone = data.get('phone', user.phone)
        user.save()
        return Response({
            'Message': 'Modified',
            'Status': status.HTTP_200_OK
        })

    def delete(self,  request):

        user1 = request.user
        user1.delete()
        return Response({
            'Message': 'deleted'
        })


class PasswordChangeApiView(APIView):
    permission_classes = [IsAuthenticated,]
    authentication_classes = [TokenAuthentication,]

    def post(self, request):
        data = request.data

        if not validate_phone(data.get('phone', '')):
            return Response({
                "Error": 'Telefon raqam xato kiritildi',
                'status': status.HTTP_400_BAD_REQUEST
            })

        user = request.user

        if user.check_password(data['old']):        # ushbu blokda userni eski paroli va data['old'] solishtirilmoqda. Yani .chek_password bazadagi va data orqali kelayotgan parollarni solishtiradi
            try:
                django_validate_password(data.get('new', ''))
            except ValidationError as e:
                return Response({
                    'Message': str(e),
                    'Status': status.HTTP_400_BAD_REQUEST
                })

            user.set_password(data['new'])
            user.save()

            return Response({
                'Message': 'Successfully changed!',
                'Status': status.HTTP_200_OK,
            })

        return Response({
            'Message': 'No changed!',
            'Status': status.HTTP_400_BAD_REQUEST,
        })


class AuthOne(APIView):
    def post(self, request):
        data = request.data
        phone = data.get('phone')

        if not data['phone']:
            return Response({
                'Error':  "Ma'lumot xato"
            })

        if not validate_phone(data.get('phone', '')):
            return Response({
                "Error": 'Telefon raqam xato kiritildi'},
                status=status.HTTP_400_BAD_REQUEST)

        code = ''.join([str(random.randint(1, 999999))[-1]  for _ in range(6)])
        int_ = string.digits
        str_ = string.ascii_letters
        letters = str(int_) + str_
        #code = ''.join([str(letters[random.randint(0, len(letters)-1)]) for _ in range(6)])
        print(code)
        key = uuid.uuid4().__str__() + '=' + code

        otp = OneTimePasswordModel.objects.create(phone=data.get('phone'), key=key)

        return Response({
            'OTP': code,
            'token': otp.key
        })


class AuthTwo(APIView):
    def post(self, request):
        data = request.data

        if not data.get('key') or not data.get('code'):
            return Response({
                'Message': 'Malumotlar xato kiritildi'
            }, status=status.HTTP_400_BAD_REQUEST)

        otp = OneTimePasswordModel.objects.filter(key=data.get('key')).first()

        if not otp:
            return Response({
                'Message': 'Bunday foydalanuvchi topilmadi, Key Xato'
            }, status=status.HTTP_400_BAD_REQUEST)

        now = datetime.datetime.now(datetime.timezone.utc)

        if (now - otp.created).total_seconds() >= 180:
            otp.is_expired = True
            otp.save()
            return Response({'Message': 'Key yaroqsiz'}, status=status.HTTP_400_BAD_REQUEST)

        if otp.is_confirmed:
            return Response({'Message': 'Key eskirgan'})

        if otp.is_expired:
            return Response({'Error': 'Key expired'}, status=status.HTTP_400_BAD_REQUEST)

        if data['code'] != data['key'][-6:]:
            otp.tried += 1
            otp.save()
            return Response({'Error': 'Xato kod kiritildi'}, status=status.HTTP_400_BAD_REQUEST)

        otp.is_confirmed = True
        otp.save()

        user = CustomUser.objects.filter(phone=otp.phone).first()
        otp = OneTimePasswordModel.objects.filter(phone=otp.phone).first()

        return Response({
            'Registered': user is not None
        }, status=status.HTTP_200_OK)


