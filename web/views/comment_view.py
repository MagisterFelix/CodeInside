from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from web.utility import convert_datetime
from web.permissions import permissions
from web.serializers import CommentSerializer
from web.models import Comment, Task, User, Achievement


class CommentView(APIView):

    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAdminUserOrIsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

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
                    comment['datetime'] = convert_datetime(comment['datetime'], request.user.time_zone)

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

                    u = User.objects.get(pk=request.user.id)
                    a = Achievement.objects.get(name='COMMENTATOR')
                    if not u.achievement.filter(name='COMMENTATOR').exists():
                        u.achievement.add(a)

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
