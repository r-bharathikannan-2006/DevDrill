from django.shortcuts import render
from . import apis

# Create your views here.
def search_template(request):
    if request.method == 'GET':
        return render(request, "search_template.html")
    elif request.method == 'POST':
        query = request.POST.get('query')
        videos_list = apis.search_video(query=query, maxResults=20)
        dictionary = {
            'videos_list':videos_list
        }
        return render(request, 'search_results.html', context=dictionary)
    
def open_player(request, video_id):
    temp = apis.generate_questions(video_id)
    dictionary = {
        'questions' : temp['questions'],
        'video_id': video_id,
        'summary': temp['summary']
    }
    return render(request, 'video_player.html', context=dictionary)


    

    





