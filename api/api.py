from .models import User, Region, District, Question, Answer
from rest_framework import serializers, viewsets
from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response


class UserSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    answer = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        """
        Override default implementation of the create method. Make sure user gets password.

        :param validated_data: the validated data sent to the method

        :return: the newly created user if successful
        """
        if self.is_valid(True):
            email = validated_data.pop("email")
            password = validated_data.pop("password")

            groups = validated_data.pop("groups")
            user_permissions = validated_data.pop("user_permissions")

            instance = User.objects.create_user(email, password=password, **validated_data)
            instance.groups.set(groups)
            instance.groups.set(user_permissions)
            return instance


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = '__all__'


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class DistrictSerializer(serializers.ModelSerializer):
    region = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = District
        fields = '__all__'


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer


class QuestionSerializer(serializers.ModelSerializer):
    answer = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # username = serializers.Field(source='user.username')
    permissions_classes = (permissions.IsAuthenticated, )

    if not settings.DEBUG:
        tag = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Question
        fields = ('user', 'region', 'anonymous', 'content', 'answer')
        # fields = ('user', 'username', 'region', 'anonymous', 'content', 'answer')


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

