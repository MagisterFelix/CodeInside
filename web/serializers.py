from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .models import User, Task, Topic, Comment, Submission, Achievement


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'name', 'birthday', 'time_zone')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=40)
    password = serializers.CharField(max_length=40, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
        JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

        email = data.get("email", None)
        password = data.get("password", None)

        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'User does not exist.')

        user = authenticate(email=email, password=password)

        if user is None:
            user = User.objects.filter(email=email).first()
            if user.check_password(password) and not user.is_active:
                raise serializers.ValidationError(
                    'User has been blocked.')
            raise serializers.ValidationError(
                'No user with this email and password was found.')

        payload = JWT_PAYLOAD_HANDLER(user)
        jwt_token = JWT_ENCODE_HANDLER(payload)
        update_last_login(None, user)
        response = {
            'email': user.email,
            'token': jwt_token
        }

        return response


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = (
            'id', 'name', 'desc'
        )
        extra_kwargs = {"name": {"required": False}}


class TaskSerializer(serializers.ModelSerializer):
    topic = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(), required=False)

    class Meta:
        model = Task
        fields = (
            'id', 'name', 'desc', 'complexity', 'topic', 'input', 'output', 'solution'
        )
        extra_kwargs = {"name": {"required": False}}


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'user', 'task', 'message', 'datetime'
        )


class SubmissionSerializer(serializers.ModelSerializer):
    language = serializers.ChoiceField(choices=['Python', 'C++', 'C#', 'Java', 'JavaScript'])

    class Meta:
        model = Submission
        fields = (
            'task', 'user', 'language'
        )

    def create(self, validated_data):
        statuses = dict((value, key) for key, value in Submission._meta.get_field('status').choices)
        languages = dict((value, key) for key, value in Submission._meta.get_field('language').choices)
        validated_data['status'] = statuses.get(validated_data['status'])
        validated_data['language'] = languages.get(validated_data['language'])
        submission = Submission.objects.create(**validated_data)
        return submission


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = (
            'name', 'desc', 'link', 'discount'
        )
