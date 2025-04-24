from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from authapp.models import CustomUser
from methodism import custom_response, MESSAGE, error_messages
from rest_framework.response import Response
from django.contrib.auth.password_validation import validate_password       # (validate_password) metodi kerakli validatsiyalarni o'tkazib, qachoki password yaroqli bo'lsa True qaytaradi




def register(request, params):
    user = request.user
    if 'phone' not in params or 'password' not in params:
        return custom_response(False, error_messages.error_params_unfilled('phone'))

    if len(params['password']) < 6 or ' ' in params['password'] or not params['password'].isalnum() \
            or not any(x.isupper() for x in params['password']):
        return custom_response(False, message={'Error': "Parol xato"})

    if len(str(params['phone'])) != 12 or not isinstance(params['phone'], int) or str(params['phone'])[:3] != '998':
        return custom_response(False, message={'Error': "Telefon xato"})

    phone = CustomUser.objects.filter(phone=params['phone']).first()
    if phone:
        return custom_response(False, message={'Error': 'User is exist'})

    user_data = {
        'phone': params['phone'],
        'password': params['password'],
        'name': params.get('name', '')
    }

    if params.get('key', '') == 'magic':  # key uchun alohida model yaratib qo'yish
        user_data.update({
            'is_active': True,
            'is_staff': True,
            'is_superuser': True,
        })
    user = CustomUser.objects.create_user(**user_data)
    print("User created:", user.pk, user.phone)
    if user.pk is None:
        return custom_response(False, error_messages.MESSAGE['user_not'])

    token = Token.objects.create(user=user)

    return custom_response(True, data={'Token': user.auth_token.key}, message={'Success': 'Registered!'})   # data={**params} --> shu qismda params ni **kwargs ko'rinishida yuborish kerak


def login(reqeust, params):

    if 'phone' not in params:
        return custom_response(False, error_messages.error_params_unfilled('phone'))

    if 'password' not in params:
        return custom_response(False, error_messages.error_params_unfilled('password'))

    user = CustomUser.objects.filter(phone=params['phone']).first()

    if not user:
        return custom_response(False, message=MESSAGE['Unauthenticated'])

    if not user.check_password(params['password']):
        return custom_response(False, message=MESSAGE['PasswordError'])

    token = Token.objects.get_or_create(user=user)

    return custom_response(True, data={'token': token[0].key }, message={'Success': "Tizimga kirdingiz!"})


def logout(request, params):
    user = request.user
    token = Token.objects.filter(user=request.user).first()
    if token:
        token.delete()
        return custom_response(True, message=MESSAGE['LogedOut'])


def get_profile_api(request, params):
    user = request.user
    return custom_response(True, data = {'data': user.format()}, message={'Success': 'User malumotlari'})


def update_profile_api(request, params):

    if len(str(params['phone'])) != 12 or not isinstance(params['phone'], int) or str(params['phone'])[:3] != '998':
        return custom_response(False, message={'Error': "Telefon xato"})

    user = request.user

    if params['phone']:
        user_ = CustomUser.objects.filter(phone=params['phone']).first()

        if user_ and user_ != user:
            return custom_response(False, message={'Error': "Ushbu raqamdan allaqachon foydalanilgan"})

        if user.phone == params['phone']:
            return custom_response(False, message={'Error': 'Bu sizning raqamingiz'})

    user.phone = params.get('phone', user.phone)
    user.name = params.get('name', user.name)
    user.save()
    return custom_response(True, message={'Success': 'Malumotlar Muvaffaqiyatli Ozgartirildi', "data": user.format()})

def delete_user_api(request, params):
    user = request.user
    print(user)
    if user.phone != params['phone']:
        user.delete()
        return custom_response(True, message=MESSAGE['UserSuccessDeleted'])
    return custom_response(False, message={'data': 'Ushbu raqam sizniki emas'})


def password_change_api(request, params):
    if len(str(params['phone'])) != 12 or not isinstance(params['phone'], int) or str(params['phone'])[:3] != '998':
        return custom_response(False, message={'Error': "Telefon xato"})

    user = request.user
    if user.check_password(params['old']):
        try:
            validate_password(params.get('new', ''))
        except ValidationError:
            return custom_response(False, message={'Error': 'Parol try blockni ichidagi validatsiyadan otmadi'})
        except Exception:
            return custom_response(False, message=MESSAGE['UndefinedError'])

        user.set_password(params.get('new'))
        user.save()
        return custom_response(True, message=MESSAGE['PasswordChanged'])

    return custom_response(False, message=MESSAGE["PasswordError"])
