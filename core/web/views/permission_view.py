from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from core.web.models import User
from core.web.permissions import permissions
from core.web.serializers import PermissionSerializer


class PermissionView(APIView):
    serializer_class = PermissionSerializer
    permission_classes = (permissions.IsAdminUser,)
    authentication_class = JSONWebTokenAuthentication

    def put(self, request, primary_key=None):
        if primary_key is None:
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'User id is required.'
        else:
            user = User.objects.filter(id=primary_key)
            if user.exists():
                serializer = self.serializer_class(user.first(), data=request.data)

                if serializer.is_valid():
                    active = serializer.validated_data.get('is_active')
                    staff = serializer.validated_data.get('is_staff')
                    if active is not None:
                        message = f'User has been {"un" * active}blocked.'
                    elif staff is not None:
                        message = f'User has {"received" if staff else "lost"} the moderator rights.'
                    else:
                        status_code = status.HTTP_400_BAD_REQUEST
                        response = {
                            'success': False,
                            'status code': status_code,
                            'message': 'One of the parameters (<is_active> or <is_staff>) must be passed.',
                        }
                        return Response(response, status=status_code)
                    serializer.save()
                    success = True
                    status_code = status.HTTP_200_OK
                else:
                    success = False
                    message = ''
                    for value in serializer.errors.values():
                        message += value[0][:-1].capitalize() + '.'
                    status_code = status.HTTP_400_BAD_REQUEST
            else:
                success = False
                status_code = status.HTTP_404_NOT_FOUND
                message = 'User does not exist.'

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
        }

        return Response(response, status=status_code)
