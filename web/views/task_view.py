from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from web.permissions import permissions
from web.serializers import TaskSerializer
from web.models import Task, Topic


class TaskView(APIView):

    serializer_class = TaskSerializer
    permission_classes = (permissions.IsAdminUserOrReadOnly,)
    authentication_class = JSONWebTokenAuthentication

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
                                                                  "complexity", "topic__name", "input", "output",
                                                                  "solution").first()
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
