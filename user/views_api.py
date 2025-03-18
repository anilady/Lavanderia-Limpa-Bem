from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from laundryadmin.models import Price
from .models import *
from .helpers import *

# Verificações de preenchimento de pedidos, senha e outros.

class RegView(APIView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_submitting'] = False
        return context

    def post(self, request):
        response = {
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Algo deu errado'
        }
        try:
            data = request.data

            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            password1 = data.get('password1')

            if not (username and email and password and password1):
                response['message'] = 'Por favor preencha todos os campos'
                response['status'] = status.HTTP_400_BAD_REQUEST
                raise ValueError('Dados incompletos')

            if password != password1:
                response['message'] = 'As senhas não correspondem'
                response['status'] = status.HTTP_400_BAD_REQUEST
                raise ValueError('As senhas não correspondem')

            # Verifique se o e-mail inserido é válido
            try:
                validate_email(email)
            except ValidationError:
                response['message'] = 'Formato de e-mail inválido'
                response['status'] = status.HTTP_400_BAD_REQUEST
                raise ValueError('Formato de e-mail inválido')

            check_user = User.objects.filter(username=username)

            if check_user.exists():
                response['message'] = 'Nome de usuário já está em uso'
                response['status'] = status.HTTP_409_CONFLICT
                raise ValueError('Nome de usuário já está em uso')

            token = generate_random_string(20)

            user_obj = User.objects.create(email=email, username=username)
            user_obj.set_password(password)
            user_obj.save()
            response['status'] = status.HTTP_201_CREATED
            response['message'] = 'User Created'

            Profile.objects.create(user=user_obj, token=token)

        except Exception as e:
            print('Exception:', str(e))

        return Response(response, status=response['status'])

RegView = RegView.as_view()

class NewRequestView(APIView):

    def post(self, request):
        user = User.objects.get(username=request.user)
        response = {
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Algo deu errado'
        }
        try:
            data = request.data

            pickup = data.get('pickup')
            topwear = data.get('topwear')
            bottomwear = data.get('bottomwear')
            woolencloth = data.get('woolencloth')
            othercloth = data.get('othercloth')
            servicetype = data.get('servicetype')
            address = data.get('address')
            mobilenumber = data.get('mobilenumber')
            description = data.get('description')
        
            if not (pickup and mobilenumber):
                response['message'] = 'Por favor preencha todos os campos'
                response['status'] = status.HTTP_400_BAD_REQUEST
                raise ValueError('Dados incompletos')

            if (servicetype == 'pickup' and address == ''):
                response['message'] = 'Por favor, preencha os campos de endereço'
                response['status'] = status.HTTP_400_BAD_REQUEST
                raise ValueError('Dados incompletos')
            
            price = Price.objects.first()
            topwearprice = int(topwear) * price.topwear
            bottomwearprice = int(bottomwear) * price.bottomwear
            woolenclothprice = int(woolencloth) * price.woolenwear

            totalprice = topwearprice + bottomwearprice + woolenclothprice 
            user_obj = UserReqeuest.objects.create(user=user, pickup_date = pickup, topwear = topwear, bottomwear=bottomwear, woolenwear=woolencloth, otherclothes=othercloth, service_type=servicetype, address=address, contact_person=mobilenumber, description=description, progress="Pending", payment="Unpaid", totalprice = totalprice, topwearprice = topwearprice, bottomwearprice = bottomwearprice, woolenwearprice = woolenclothprice)
            user_obj.save()

            response = {
                'status': status.HTTP_201_CREATED,
                'message': 'Solicitação enviada pelo usuário com sucesso'
            }

        except Exception as e:
            print('Exception:', str(e))

        return Response(response, status=response['status'])

NewRequestView = NewRequestView.as_view()