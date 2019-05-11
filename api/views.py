from .serializers import (
    UserSerializer,
    RegionSerializer,
    DistrictSerializer,
    QuestionSerializer,
    AnswerSerializer,
    CategorySerializer,
    CreateUserSerializer,
    LoginUserSerializer,
)
from .models import (
    User,
    Region,
    District,
    Question,
    Answer,
    Category
)
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from .tokens import TokenSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer
    permissions_classes = (permissions.AllowAny, )

    def post(self, request, *args, **kwargs):
        '''
        :param request: must have username, email, password
        :return: user and token
        '''
        if len(request.data["username"]) < 2:
            body = {"message": "short username"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        if len(request.data["password"]) < 6:
            body = {"message": "short password"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": TokenSerializer(user).token,
            }
        )


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": TokenSerializer(user).token,
            }
        )


class UserAPI(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class QuestionAPI(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuestionSerializer

    def get_object(self, pk):
        return Question.objects.get(pk=pk)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            {
                "result": QuestionSerializer(
                    instance, context=self.get_serializer_context()
                ).data
            })

    def patch(self, request):
        pk = request.data["pk"]
        instance = self.get_object(pk)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(
            status=204,
            data={
                "result": QuestionSerializer(response).data
            })


class AnswerAPI(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AnswerSerializer

    def get_object(self, pk):
        return Answer.objects.get(pk=pk)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            {
                "result": AnswerSerializer(
                    instance, context=self.get_serializer_context()
                ).data
            }
        )

    def patch(self, request):
        pk = request.data["pk"]
        instance = self.get_object(pk)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(
            status=204,
            data={
                "result": AnswerSerializer(response).data
            })


class ChangeBoolAPI(generics.UpdateAPIView):

    def change_bool(self, request, field, *args, **kwargs):
        from django.forms.models import model_to_dict
        instance = self.get_object(self.kwargs['pk'])
        _dict = model_to_dict(instance)
        _dict[field] = not _dict[field]
        serializer = self.get_serializer(instance, partial=True, data=_dict)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return response

    @staticmethod
    def __error_invalid_request_user(request, authorized_user_id):
        if request.user.id != authorized_user_id:
            body = {"message": "invalid user to request"}
            return Response(body, status=status.HTTP_403_FORBIDDEN)


class SelectAnswerAPI(ChangeBoolAPI):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AnswerSerializer
    question_serializer = QuestionSerializer

    def get_queryset(self):
        return Answer.objects.filter(pk=self.kwargs['pk']).first()

    def get_object(self, pk):
        return Answer.objects.get(pk=pk)

    @staticmethod
    def get_question(pk):
        return Question.objects.get(pk=pk)

    def post(self, request, *args, **kwargs):
        body = {"message": ''}
        answer = self.get_object(self.kwargs['pk'])

        self.__error_invalid_request_user(request, authorized_user_id=answer.question.user_id)

        question = self.get_question(pk=answer.question_id)
        if question.has_selected_answer:
            body["message"] = "already selected another answer"
            return Response(body, status=status.HTTP_406_NOT_ACCEPTABLE)

        if answer.is_selected:
            body["message"] = "the answer is already selected"
            return Response(body, status=status.HTTP_406_NOT_ACCEPTABLE)

        response = self.change_bool(request, field='is_selected')
        question.has_selected_answer = True
        question.save()
        return Response(
            status=204,
            data={
                "result": AnswerSerializer(response).data
            })


# TODO : request.data['user'] = request.user.id -> decorator로 처리

class RecentQuestionAPI()