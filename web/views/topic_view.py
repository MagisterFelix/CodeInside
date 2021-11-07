from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from web.permissions import permissions
from web.serializers import TopicSerializer
from web.models import Topic


class TopicView(APIView):

    serializer_class = TopicSerializer
    permission_classes = (permissions.IsAdminUserOrReadOnly,)
    authentication_class = JSONWebTokenAuthentication

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
