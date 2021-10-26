from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .permissions import permissions
from .serializers import UserRegistrationSerializer, UserLoginSerializer, TaskSerializer, TopicSerializer
from .models import User, Task, Topic


class UserRegistrationView(CreateAPIView):

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
        }

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
            'data': data
        }

        return Response(response, status=status_code)


class TaskView(APIView):

    serializer_class = TaskSerializer
    http_method_names = ['post', 'get', 'put', 'delete', 'options']
    permission_classes = (permissions.IsAdminUserOrReadOnly,)

    def post(self, request):
        if request.data.get('name') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Task must have a name.'
        else:
            topic_name = request.data.get('topic')
            if Topic.objects.filter(name=topic_name).exists():
                request.data['topic'] = Topic.objects.get(
                    name=topic_name).pk

                serializer = self.serializer_class(data=request.data)

                if serializer.is_valid():
                    serializer.save()
                    success = True
                    status_code = status.HTTP_201_CREATED
                    message = 'Task created successfully.'
                else:
                    success = False
                    message = ''
                    for value in serializer.errors.values():
                        message += value[0][:-1].capitalize() + '.'
                    status_code = status.HTTP_400_BAD_REQUEST
            else:
                success = False
                message = 'Topic does not exist.'
                status_code = status.HTTP_404_NOT_FOUND

        response = {
            'success': success,
            'status code': status_code,
            'message': message
        }

        return Response(response, status=status_code)

    def get(self, request):
        if request.data.get('name') is None:
            data = Task.objects.all().values("id", "name", "desc",
                                             "complexity", "topic__name", "input", "output", "solution")
            success = True
            status_code = status.HTTP_200_OK
            message = 'Tasks received successfully.'
        else:
            task_name = request.data['name']
            if Task.objects.filter(name=task_name).exists():
                data = Task.objects.filter(name=task_name).values("id", "name", "desc",
                                                                  "complexity", "topic__name", "input", "output", "solution").first()
                success = True
                status_code = status.HTTP_200_OK
                message = 'Task received successfully.'
            else:
                data = None
                success = False
                status_code = status.HTTP_404_NOT_FOUND
                message = 'Task does not exist.'

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
            'data': data
        }

        return Response(response, status=status_code)

    def put(self, request):
        if request.data.get('id') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Task id is required.'
        else:
            topic = request.data.get('topic')
            if topic:
                topic = Topic.objects.filter(name=topic)
                if topic.exists():
                    request.data['topic'] = topic.first().pk
                else:
                    status_code = status.HTTP_404_NOT_FOUND
                    return Response({
                        'success': False,
                        'status code': status_code,
                        'message': 'Topic does not exist.'
                    }, status=status_code)

            serializer = self.serializer_class(Task.objects.get(
                id=request.data['id']), data=request.data)

            if serializer.is_valid():
                serializer.save()
                success = True
                status_code = status.HTTP_200_OK
                message = 'Task updated successfully.'
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

    def delete(self, request):
        if request.data.get('name') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Task name is required.'
        else:
            task = Task.objects.filter(name=request.data['name'])
            if task.exists():
                Task.objects.filter(name=request.data['name']).delete()
                success = True
                status_code = status.HTTP_200_OK
                message = 'Task deleted successfully.'
            else:
                success = False
                status_code = status.HTTP_404_NOT_FOUND
                message = 'Task does not exist.'

        response = {
            'success': success,
            'status code': status_code,
            'message': message
        }

        return Response(response, status=status_code)


class TopicView(APIView):

    serializer_class = TopicSerializer
    http_method_names = ['post', 'get', 'put', 'delete', 'options']
    permission_classes = (permissions.IsAdminUserOrReadOnly,)

    def post(self, request):
        if request.data.get('name') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Topic must have a name.'
        else:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                serializer.save()
                success = True
                status_code = status.HTTP_201_CREATED
                message = 'Topic created successfully.'
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

    def get(self, request):
        if request.data.get('name') is None:
            data = Topic.objects.all().values()
            success = True
            status_code = status.HTTP_200_OK
            message = 'Topics received successfully.'
        else:
            topic = Topic.objects.filter(name=request.data['name'])
            if topic.exists():
                data = topic.values().first()
                success = True
                status_code = status.HTTP_200_OK
                message = 'Topic received successfully.'
            else:
                data = None
                success = False
                status_code = status.HTTP_404_NOT_FOUND
                message = 'Topic does not exist.'

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
            'data': data
        }

        return Response(response, status=status_code)

    def put(self, request):
        if request.data.get('id') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Topic id is required.'
        else:
            serializer = self.serializer_class(Topic.objects.get(
                id=request.data['id']), data=request.data)

            if serializer.is_valid():
                serializer.save()
                success = True
                status_code = status.HTTP_200_OK
                message = 'Topic updated successfully.'
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

    def delete(self, request):
        if request.data.get('name') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Topic name is required.'
        else:
            topic = Topic.objects.filter(name=request.data['name'])
            if topic.exists():
                Topic.objects.filter(name=request.data['name']).delete()
                success = True
                status_code = status.HTTP_200_OK
                message = 'Topic deleted successfully.'
            else:
                success = False
                status_code = status.HTTP_404_NOT_FOUND
                message = 'Topic does not exist.'

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
        }

        return Response(response, status=status_code)
