from .models import User, Region, District, Question, Answer, Category, QuestionVote
from rest_framework import serializers, status
from django.conf import settings
from rest_framework import permissions
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    # question = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # answer = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ('password',)


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
        if user is None:
            validation_error = serializers.ValidationError
            validation_error.status_code = status.HTTP_404_NOT_FOUND
            raise serializers.ValidationError(
                code='Not Found',
                detail={"error": "이메일 또는 비밀번호가 올바르지 않습니다."}
            )

        if user.is_active is False:
            validation_error = serializers.ValidationError
            validation_error.status_code = status.HTTP_404_NOT_FOUND
            raise serializers.ValidationError(
                code='Unavailable',
                detail={"error": "이용할 수 없는 회원입니다. 고객센터에 연락해주세요."}
            )

        return user


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
    user_name = serializers.ReadOnlyField(source='user.username')
    user_avatar = serializers.SerializerMethodField('get_photo_url')
    user_is_active = serializers.ReadOnlyField(source='user.is_active')
    region_name = serializers.CharField(source='region.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    selected_answer_text = serializers.CharField(source='selected_answer.text', read_only=True)

    class Meta:
        model = Question
        exclude = ('region',)

    def get_photo_url(self, obj):
        try:
            request = self.context.get('request')
        except AttributeError:
            request = self.context
        avatar_url = obj.user.avatar.url
        return request.build_absolute_uri(avatar_url)


class AnswerSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    user_avatar = serializers.SerializerMethodField('get_photo_url')

    class Meta:
        model = Answer
        fields = '__all__'

    def get_photo_url(self, obj):
        request = self.context.get('request')
        avatar_url = obj.user.avatar.url
        return request.build_absolute_uri(avatar_url)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class QuestionVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionVote
        fields = '__all__'
        extra_kwargs = {
            "updated_at": {"read_only": True},
            "created_at": {"read_only": True}
        }