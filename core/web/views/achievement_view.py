from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from core.web.models import Achievement
from core.web.permissions import permissions
from core.web.serializers import AchievementSerializer


class AchievementView(APIView):
    serializer_class = AchievementSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request):
        user_achievements = self.request.user.achievement.values()
        other_achievements = Achievement.objects.difference(user_achievements).values()

        for achievement in user_achievements:
            achievement['earned'] = True
        for achievement in other_achievements:
            achievement['earned'] = False

        data = list(user_achievements) + list(other_achievements)
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
