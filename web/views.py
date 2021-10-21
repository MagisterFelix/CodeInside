from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .models import User


class UserRegistrationView(CreateAPIView):

    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        if request.data.get('email') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'User must have an email.'
        elif request.data.get('password') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'User must have a password.'
        else:
            if request.data.get('birthday') is not None:
                month, day, year = request.data['birthday'].split('/')
                request.data['birthday'] = f'{year}-{month}-{day}'

            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                serializer.save()
                success = True
                status_code = status.HTTP_201_CREATED
                message = 'User registered successfully.'
            else:
                success = False
                message = ''
                for value in serializer.errors.values():
                    message += value[0][:-1].capitalize() + '.'
                status_code = status.HTTP_400_BAD_REQUEST

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
        }

        return Response(response, status=status_code)


class UserLoginView(RetrieveAPIView):

    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        if request.data.get('email') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'User must have an email.'
            token = None
        elif request.data.get('password') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'User must have a password.'
            token = None
        else:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                success = True
                status_code = status.HTTP_200_OK
                message = 'User logged in successfully.'
                token = serializer.data['token']
            else:
                success = False
                message = ''
                for value in serializer.errors.values():
                    message += value[0][:-1].capitalize() + '.'
                status_code = status.HTTP_404_NOT_FOUND
                if message == 'User has been blocked.':
                    status_code = status.HTTP_403_FORBIDDEN
                token = None

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
            'token': token
        }

        return Response(response, status=status_code)


class UserProfileView(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request):
        user = User.objects.get(email=request.user)
        role = 'Admin' if user.is_superuser else 'Moderator' if user.is_staff else 'User'
        banned = not user.is_active
        birthday = user.birthday.strftime(
            r'%m/%d/%Y') if user.birthday else None

        success = True
        status_code = status.HTTP_200_OK
        message = 'User profile received successfully.'
        data = {
            'name': user.name,
            'role': role,
            'banned': banned,
            'premium': user.premium,
            'birthday': birthday,
        }

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
            'data': data
        }

        return Response(response, status=status_code)
