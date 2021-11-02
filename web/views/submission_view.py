from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from web.utility import WithChoices, convert_datetime
from web.permissions import permissions
from web.serializers import SubmissionSerializer
from web.models import Submission, Task


class SubmissionView(APIView):

    serializer_class = SubmissionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request, primary_key=None):
        if primary_key is None:
            data = Submission.objects.all()\
                .annotate(lang=WithChoices(Submission, "language"), result=WithChoices(Submission, "status")) \
                .values("id", "task__name", "user__name", "result", "datetime", "lang", "time", "memory")
            for submission in data:
                submission['datetime'] = convert_datetime(submission['datetime'], request.user.time_zone)
            success = True
            status_code = status.HTTP_200_OK
            message = 'Submissions received successfully.'
        else:
            if Submission.objects.filter(id=primary_key).exists():
                data = Submission.objects.filter(id=primary_key) \
                    .annotate(lang=WithChoices(Submission, "language"), result=WithChoices(Submission, "status")) \
                    .values("id", "task__name", "user__name", "result", "datetime", "lang", "time", "memory")
                submission['datetime'] = convert_datetime(submission['datetime'], request.user.time_zone)
                success = True
                status_code = status.HTTP_200_OK
                message = 'Submission received successfully.'
            else:
                data = None
                success = False
                status_code = status.HTTP_404_NOT_FOUND
                message = 'Submission does not exist.'

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
            'data': data
        }

        return Response(response, status=status_code)
