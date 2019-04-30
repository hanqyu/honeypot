from django.shortcuts import render
# from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

# def update_profile(request, user_id):
#     user = User.objects.get(pk=user_id)
#     user.bio = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit...'
#     user.save()

def recent_question(request):
    '''
    :param current_user_id: 접속 중인 user의 id, 일단 지금은 출력할 유저의 sample
    :return: render
    '''

    # if 'get_recent_question' in request.POST:
    current_user = User.objects.first()
    context = {}
    context['user'] = current_user
    context['user_avatar_url'] = current_user.avatar.url

    question = Question.objects.first()
    context['question_text'] = question.content
    context['question_region'] = Region.objects.get(pk=question.region_id).name
    context['question_answered_count'] = question.answered_count

    return render(request, 'index.html', context)

    payload = {'id': 2}
    headers = {'content-type': 'application/json'}
    url = "https://www.toggl.com/api/v6/" + data_description + ".json"
    response = requests.delete(url, data=json.dumps(payload), headers=headers)
