from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from core.web.models import User, Achievement
from core.web.permissions import permissions
from core.web.serializers import UserRegistrationSerializer, UserLoginSerializer, ProfileSerializer


LOGIN_FAILS = {
    'email': 'User must have an email.',
    'password': 'User must have a password.'
}
REGISTRATION_FAILS = {
    **LOGIN_FAILS,
    'time_zone': 'Time zone is required.'
}


class UserRegistrationView(APIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        for key, value in REGISTRATION_FAILS.items():
            if request.data.get(key) is None:
                success = False
                status_code = status.HTTP_400_BAD_REQUEST
                message = value
                break
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
        for key, value in LOGIN_FAILS.items():
            if request.data.get(key) is None:
                success = False
                status_code = status.HTTP_400_BAD_REQUEST
                message = value
                token = None
                break
        else:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                success = True
                status_code = status.HTTP_200_OK
                message = 'User logged in successfully.'
                token = serializer.data['token']

                user = User.objects.get(email=request.data.get('email'))
                acquaintance_achievement = Achievement.objects.get(name='ACQUAINTANCE')
                if not user.achievement.filter(name='ACQUAINTANCE').exists():
                    user.achievement.add(acquaintance_achievement)

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
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request):
        user = User.objects.get(email=request.user)
        role = 'Admin' if user.is_superuser else 'Moderator' if user.is_staff else 'User'
        premium = bool(user.premium)
        banned = not user.is_active
        birthday = user.birthday.strftime(
            r'%m/%d/%Y') if user.birthday else None

        success = True
        status_code = status.HTTP_200_OK
        message = 'User profile received successfully.'
        data = {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': role,
            'image': user.image,
            'banned': banned,
            'premium': premium,
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

    def put(self, request):
        user = User.objects.get(email=request.user)

        if request.data.get('birthday') is not None:
            month, day, year = request.data['birthday'].split('/')
            request.data['birthday'] = f'{year}-{month}-{day}'

        serializer = self.serializer_class(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            success = True
            status_code = status.HTTP_200_OK
            message = 'User updated successfully.'
            for key in ('password', 'image'):
                if request.data.get(key):
                    message = f'User {key} updated successfully.'
        else:
            success = False
            message = ''
            for value in serializer.errors.values():
                message += value[0][:-1].capitalize() + '.'
            status_code = status.HTTP_400_BAD_REQUEST

        response = {
            'success': success,
            'status code': status_code,
            'message': message
        }

        return Response(response, status=status_code)
