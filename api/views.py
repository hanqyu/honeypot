from .serializers import (
    UserSerializer,
    RegionSerializer,
    DistrictSerializer,
    QuestionSerializer,
    AnswerSerializer,
    CategorySerializer,
    CreateUserSerializer,
    LoginUserSerializer,
    QuestionVoteSerializer
)
from .models import (
    User,
    Region,
    District,
    Question,
    Answer,
    Category,
    QuestionVote
)
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, APIException
from django.core.exceptions import ObjectDoesNotExist
from .tokens import TokenSerializer
from django.forms.models import model_to_dict
from django.db.models import Count


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


class QuestionVoteViewSet(viewsets.ModelViewSet):
    queryset = QuestionVote.objects.all()
    serializer_class = QuestionVoteSerializer


class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer
    permissions_classes = (permissions.AllowAny,)

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
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    @staticmethod
    def __error_invalid_request_user(requested_user_id, authorized_user_id):
        if int(requested_user_id) != int(authorized_user_id):
            message = "invalid user to request"
            raise PermissionDenied(message)

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        self.__error_invalid_request_user(request.user.id, authorized_user_id=kwargs.get('pk'))
        if request.data['category']:
            for category_id in request.data['category']:
                try:
                    Category.objects.get(id=category_id)
                except ObjectDoesNotExist:
                    raise APIException('Given categories is not correct.')

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(
            status=204,
            data={
                "message": "유저 정보가 업데이트 되었습니다.",
                "result": UserSerializer(response, context=self.get_serializer_context()).data
            }
        )


class QuestionAPI(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()

    def post(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            {
                "result": QuestionSerializer(
                    instance, context=self.get_serializer_context()
                ).data
            })

    def patch(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        request.data['user'] = request.user.id
        self.queryset = Question.objects.filter(pk=pk).all()
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(
            status=204,
            data={
                "message": "질문이 수정되었습니다",
                "result": QuestionSerializer(response, context=self.get_serializer_context()).data
            })

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        if pk:
            self.queryset = Question.objects.filter(pk=pk).all()
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        result = serializer.data

        return Response(
            status=200,
            data={
                "count": len(result),
                "result": result
            })


class AnswerInQuestionAPI(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuestionSerializer
    answer_serializer = AnswerSerializer

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        self.queryset = Question.objects.filter(pk=pk).all()
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        answers = Answer.objects.filter(pk__in=serializer.data['answer']).all()
        question = {
            "id": instance.id,
            "text": instance.text,
            "created_at": instance.created_at,
            "has_selected_answer": instance.has_selected_answer,
        }
        if instance.has_selected_answer:
            question['selected_answer'] = instance.selected_answer.id
        result = AnswerSerializer(answers, context=self.get_serializer_context(), many=True).data

        return Response(
            status=200,
            data={
                "question": question,
                "count": len(result),
                "result": result
            })


class AnswerAPI(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AnswerSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            {
                "result": AnswerSerializer(
                    instance, context=self.get_serializer_context()
                ).data
            }
        )

    def patch(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        self.queryset = Answer.objects.filter(pk=pk).all()
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(
            status=204,
            data={
                "result": AnswerSerializer(response, context=self.get_serializer_context()).data
            })


class ChangeBoolAPI(generics.UpdateAPIView):

    def change_bool(self, request, field, *args, **kwargs):
        instance = self.get_object()
        _dict = model_to_dict(instance)
        _dict[field] = not _dict[field]
        serializer = self.get_serializer(instance, partial=True, data=_dict)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return response


class SelectAnswerAPI(ChangeBoolAPI):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AnswerSerializer
    question_serializer = QuestionSerializer

    @staticmethod
    def get_question(pk):
        return Question.objects.get(pk=pk)

    @staticmethod
    def __error_invalid_request_user(requested_user_id, authorized_user_id):
        if int(requested_user_id) != int(authorized_user_id):
            message = "invalid user to request"
            raise PermissionDenied(message)

    def post(self, request, *args, **kwargs):
        body = {"message": ''}
        pk = kwargs.get('pk')
        self.queryset = Answer.objects.filter(pk=pk).all()
        answer = self.get_object()

        self.__error_invalid_request_user(request.user.id, authorized_user_id=answer.question.user_id)

        question = self.get_question(pk=answer.question_id)
        if question.has_selected_answer:
            body["message"] = "already selected another answer"
            return Response(body, status=status.HTTP_406_NOT_ACCEPTABLE)

        if answer.is_selected:
            body["message"] = "the answer is already selected"
            return Response(body, status=status.HTTP_406_NOT_ACCEPTABLE)

        response = self.change_bool(request, field='is_selected')
        question.has_selected_answer = True
        question.selected_answer = answer
        question.save()
        return Response(
            status=204,
            data={
                "result": AnswerSerializer(response, context=self.get_serializer_context()).data
            })


# TODO : request.data['user'] = request.user.id -> decorator로 처리

class RecentQuestionAPI(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    max_count = 30

    def get_queryset(self):
        category = self.kwargs.get('category')
        if category:
            self.queryset = self.queryset.filter(category=category)
        return self.queryset.order_by('-created_at')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset().all()

        if self.kwargs.get('count'):
            count = min(self.kwargs.get('count'), self.max_count)
        else:
            count = self.max_count
        queryset = queryset[:count].all()
        serializer = self.get_serializer(queryset, context=self.get_serializer_context(), many=True)

        result = serializer.data
        requested_user_id = request.user.id

        for idx, question in enumerate(result):
            print(question['id'])
            question = Question.objects.get(pk=int(question['id']))
            requested_user_voted_or_not = question.get_requested_user_voted_or_not(requested_user_id)
            result[idx]['requested_user_voted'] = requested_user_voted_or_not

        return Response(
            status=200,
            data={
                "count": len(result),
                "result": result
            }
        )


class PopularQuestionAPI(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    max_count = 30

    def get_queryset(self):
        category = self.kwargs.get('category')
        if category:
            self.queryset = self.queryset.filter(category=category)
        return self.queryset.annotate(voting_count=Count('question_vote')).order_by('-voting_count')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset().all()

        if self.kwargs.get('count'):
            count = min(self.kwargs.get('count'), self.max_count)
        else:
            count = self.max_count
        queryset = queryset[:count]
        serializer = self.get_serializer(queryset, context=self.get_serializer_context(), many=True)
        result = serializer.data

        return Response(
            status=200,
            data={
                "count": len(result),
                "result": result
            }
        )


class PreferredQuestionAPI(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    max_count = 30

    def get_queryset(self):
        return self.queryset.order_by('-created_at')

    def get(self, request, *args, **kwargs):
        queryset_append = self.get_queryset().all()

        category = request.user.category
        self.queryset = self.queryset.filter(category__in=category)
        queryset = self.get_queryset().all()

        if self.kwargs.get('count'):
            count = min(self.kwargs.get('count'), self.max_count)
        else:
            count = self.max_count

        serializer = self.get_serializer(queryset, context=self.get_serializer_context(), many=True)
        result = serializer.data

        serializer = self.get_serializer(queryset_append, context=self.get_serializer_context(), many=True)
        result += serializer.data

        result = result[::-1][:count]

        response = {
            "count": len(result),
            "result": result
        }

        if len(category) is 0:
            response["message"] = "선호 카테고리를 등록해주세요."

        return Response(
            status=200,
            data=response
        )


class VoteQuestionAPI(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuestionVoteSerializer

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        self.queryset = Question.objects.filter(pk=pk).all()
        question = self.get_object()
        request.data['question'] = question.id
        request.data['user_questioned'] = question.user_id
        request.data['user_voted'] = request.user.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        instance, created = QuestionVote.objects.get_or_create(
            question_id=validated_data['question'].id,
            user_questioned_id=validated_data['user_questioned'].id,
            user_voted_id=validated_data['user_voted'].id
        )

        if created:
            response = {
                'new_created': created,
                'result': self.get_serializer(
                    instance, context=self.get_serializer_context()
                ).data
            }

        else:
            instance.delete()
            response = {
                'deleted': True,
                'message': 'boost가 취소되었습니다.'
            }

        return Response(response)
