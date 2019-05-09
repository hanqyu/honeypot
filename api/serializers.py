from .models import User, Region, District, Question, Answer, Category
from rest_framework import serializers
from django.conf import settings
from rest_framework import permissions
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    # question = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # answer = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        # fields = ('id', 'email', 'username')


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password')
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """
        Override default implementation of the create method. Make sure user gets password.

        :param validated_data: the validated data sent to the method

        :return: the newly created user if successful
        """
        if self.is_valid(True):
            email = validated_data.pop("email")
            password = validated_data.pop("password")

            # groups = validated_data.pop("groups")
            # user_permissions = validated_data.pop("user_permissions")

            instance = User.objects.create_user(email, password=password, **validated_data)
            # instance.groups.set(groups)
            # instance.groups.set(user_permissions)
            return instance


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")


class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = '__all__'


class DistrictSerializer(serializers.ModelSerializer):
    region = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = District
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    answer = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # username = serializers.Field(source='user.username')

    if not settings.DEBUG:
        tag = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Question
        fields = ('user', 'region', 'anonymous', 'text', 'answer')
        # fields = ('user', 'username', 'region', 'anonymous', 'text', 'answer')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'