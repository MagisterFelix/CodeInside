from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from web.utility import WithChoices, convert_datetime
from web.permissions import permissions
from web.serializers import SubmissionSerializer
from web.models import Submission, Task
from web.checker import Checker


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
            if Task.objects.filter(id=primary_key).exists():
                data = Submission.objects.filter(task=primary_key) \
                    .annotate(lang=WithChoices(Submission, "language"), result=WithChoices(Submission, "status")) \
                    .values("id", "task__name", "user__name", "result", "datetime", "lang", "time", "memory")

                for submission in data:
                    submission['datetime'] = convert_datetime(submission['datetime'], request.user.time_zone)

                success = True
                status_code = status.HTTP_200_OK
                message = 'Submissions received successfully.'
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
            data = None
            success = False
            status_code = status.HTTP_400_BAD_REQUEST
            message = 'Submission must be tied to task.'
        else:
            task_name = request.data.get('task')
            if Task.objects.filter(name=task_name).exists():
                task = Task.objects.get(name=task_name)

                request.data['task'] = task.pk
                request.data['user'] = request.user.id

                serializer = self.serializer_class(data=request.data)

                if serializer.is_valid():
                    checker = Checker(request.user, task, request.data['language'], request.data['code'])
                    checker.check()

                    data = checker.get_data()
                    serializer.save(**data)
                    data['message'] = checker.message
                    success = True
                    status_code = status.HTTP_201_CREATED
                    message = 'Submission created successfully.'
                else:
                    data = None
                    success = False
                    message = ''
                    for value in serializer.errors.values():
                        message += value[0][:-1].capitalize() + '.'
                    status_code = status.HTTP_400_BAD_REQUEST
            else:
                data = None
                success = False
                message = 'Task does not exist.'
                status_code = status.HTTP_404_NOT_FOUND

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
            'data': data
        }

        return Response(response, status=status_code)