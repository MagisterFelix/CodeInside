from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from web.permissions import permissions
from web.serializers import UserRegistrationSerializer, UserLoginSerializer
from web.models import User, Achievement


class UserRegistrationView(APIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        if request.data.get('email') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'User must have an email.'
        elif request.data.get('password') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'User must have a password.'
        elif request.data.get('time_zone') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Time zone is required.'
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


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = (permissions.AllowAny,)

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

                u = User.objects.get(email=request.data.get('email'))
                a = Achievement.objects.get(name='ACQUAINTANCE')
                if not u.achievement.filter(name='ACQUAINTANCE').exists():
                    u.achievement.add(a)

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


class UserProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
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
            'time_zone': user.time_zone
        }

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
            'data': data
        }

        return Response(response, status=status_code)
