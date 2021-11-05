from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from web.permissions import permissions
from web.serializers import AchievementSerializer
from web.models import Achievement


class AchievementView(APIView):
    serializer_class = AchievementSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request):
        u = self.request.user.achievement.values()
        a = Achievement.objects.all()

        for i in u:
            i['earned'] = True
            a = a.exclude(name=i['name'])
        a = a.values()
        for i in a:
            i['earned'] = False

        data = list(u) + list(a)
        success = True
        status_code = status.HTTP_200_OK
        message = 'Achievements received successfully.'

        response = {
            'success': success,
            'status code': status_code,
            'message': message,
            'data': data
        }

        return Response(response, status=status_code)
