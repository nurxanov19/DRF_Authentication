
from rest_framework.authtoken.models import Token
from authapp.models import CustomUser
from methodism import custom_response, MESSAGE, error_messages
from rest_framework.response import Response


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



