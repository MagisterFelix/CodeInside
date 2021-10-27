from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from pytz import timezone

from .permissions import permissions
from .serializers import UserRegistrationSerializer, UserLoginSerializer, TaskSerializer, TopicSerializer, CommentSerializer
from .models import User, Task, Topic, Comment


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


class TopicView(APIView):

    serializer_class = TopicSerializer
    permission_classes = (permissions.IsAdminUserOrReadOnly,)

    def get(self, request, primary_key=None):
        if primary_key is None:
            data = Topic.objects.all().values()
            success = True
            status_code = status.HTTP_200_OK
            message = 'Topics received successfully.'
        else:
            topic = Topic.objects.filter(id=primary_key)
            if topic.exists():
                data = topic.values("name", "desc").first()
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

    def put(self, request, primary_key=None):
        if primary_key is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Topic id is required.'
        else:
            topic = Topic.objects.filter(id=primary_key)
            if topic.exists():
                serializer = self.serializer_class(
                    topic.first(), data=request.data)

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
            else:
                success = False
                status_code = status.HTTP_404_NOT_FOUND
                message = 'Topic does not exist.'

        response = {
            'success': success,
            'status code': status_code,
            'message': message
        }

        return Response(response, status=status_code)

    def delete(self, request, primary_key=None):
        if primary_key is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Topic id is required.'
        else:
            topic = Topic.objects.filter(id=primary_key)
            if topic.exists():
                Topic.objects.filter(id=primary_key).delete()
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


class TaskView(APIView):

    serializer_class = TaskSerializer
    permission_classes = (permissions.IsAdminUserOrReadOnly,)

    def get(self, request, primary_key=None):
        if primary_key is None:
            data = Task.objects.all().values("id", "name", "desc",
                                             "complexity", "topic__name", "input", "output", "solution")
            success = True
            status_code = status.HTTP_200_OK
            message = 'Tasks received successfully.'
        else:
            if Task.objects.filter(id=primary_key).exists():
                data = Task.objects.filter(id=primary_key).values("name", "desc",
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

    def put(self, request, primary_key=None):
        if primary_key is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Task id is required.'
        else:
            task = Task.objects.filter(id=primary_key)
            if task.exists():
                topic = request.data.get('topic')
                if topic is not None:
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

                serializer = self.serializer_class(
                    Task.objects.get(id=primary_key), data=request.data)

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

    def delete(self, request, primary_key=None):
        if primary_key is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Task id is required.'
        else:
            task = Task.objects.filter(id=primary_key)
            if task.exists():
                Task.objects.filter(id=primary_key).delete()
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


class CommentView(APIView):

    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAdminUserOrIsAuthenticated,)

    def get(self, request, primary_key=None):
        if primary_key is None:
            data = None
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Task id is required.'
        else:
            task = Task.objects.filter(id=primary_key)
            if task.exists():
                data = Comment.objects.filter(
                    task=primary_key).values("id", "user__name", "message", "datetime")

                for comment in data:
                    comment['datetime'] = comment['datetime'].astimezone(timezone(request.user.time_zone)).strftime(
                        '%m/%d/%Y %H:%M')

                success = True
                status_code = status.HTTP_200_OK
                message = 'Comments received successfully.'
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

    def post(self, request):
        if request.data.get('task') is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Comment must be tied to task.'
        else:
            request.data['user'] = request.user.id
            task_name = request.data.get('task')
            if Task.objects.filter(name=task_name).exists():
                request.data['task'] = Task.objects.get(
                    name=task_name).pk

                serializer = self.serializer_class(data=request.data)

                if serializer.is_valid():
                    serializer.save()
                    success = True
                    status_code = status.HTTP_201_CREATED
                    message = 'Comment created successfully.'
                else:
                    success = False
                    message = ''
                    for value in serializer.errors.values():
                        message += value[0][:-1].capitalize() + '.'
                    status_code = status.HTTP_400_BAD_REQUEST
            else:
                success = False
                message = 'Task does not exist.'
                status_code = status.HTTP_404_NOT_FOUND

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
        }

        return Response(response, status=status_code)

    def delete(self, request, primary_key=None):
        if primary_key is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Comment id is required.'
        else:
            comment = Comment.objects.filter(id=primary_key)
            if comment.exists():
                comment.delete()
                success = True
                status_code = status.HTTP_200_OK
                message = 'Comment deleted successfully.'
            else:
                success = False
                status_code = status.HTTP_404_NOT_FOUND
                message = 'Comment does not exist.'

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
        }

        return Response(response, status=status_code)
