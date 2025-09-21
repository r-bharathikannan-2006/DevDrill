import requests
import json
import re
from youtube_transcript_api import YouTubeTranscriptApi
import os

def parse_duration(iso_string):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_string)
    if not match:
        return "N/A"
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0:
        parts.append(f"{seconds}s")
        
    return " ".join(parts) if parts else "0s"

# Example usage with duration from the API
duration_string = "PT12H"
readable_duration = parse_duration(duration_string)
print(f"Readable Duration: {readable_duration}") # Output: Readable Duration: 12h


# Youtube search
def search_video(query, maxResults=10):
    """Returns the list of related videos.  Each video object is a dictionary with video_id, title, url as keys."""
    API_KEY = os.environ['API_KEY_SEARCH']
    search_url = "https://www.googleapis.com/youtube/v3/search"
    videos_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        'key': API_KEY,
        'q': query,
        'part': 'snippet',
        'type':'video',
        'maxResults': maxResults,
        'videoCaption': 'closedCaption',
        'type': 'video',
        'relevanceLanguage': 'en',
        'safeSearch': 'strict',
    }
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        data = response.json()
        videos = []
        for item in data.get("items", []):
            video_params = {
            'key': API_KEY,
            'id': item["id"]["videoId"],
            'part': 'contentDetails',
            }

            video_response = requests.get(videos_url, params=video_params)

            if video_response.status_code == 200:
                video_data = video_response.json()
                items = video_data.get("items", [])
                if items:
                    duration = items[0]['contentDetails']['duration']
            duration = parse_duration(duration)
            video = {
                 'video_id' : item["id"]["videoId"],
                 'title' : item['snippet']['title'],
                 'url': f"https://www.youtube.com/watch?v={item["id"]["videoId"]}",
                 'duration': duration,
                 'channel': item['snippet']['channelTitle']
            }
            videos.append(video)
        print(item)
        return videos
    else:
         print(f"Error : {response.status_code}, {response.text} while Searching for videos")
         return None


def generate_questions(video_id):
    """Return list of dictionary which represents question as:
        - "question": The quiz question.
        - 1: Option 1
        - 2: Option 2
        - 3: Option 3
        - 4: Option 4
        - "correct": The option number of the correct option.
    """
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id, languages=['en'])
    try:
        transcript = ytt_api.fetch(video_id, languages=['en'])
        full_transript = ""
        for segment in transcript:
            full_transript += (segment.text + " ")
    except Exception as e:
        print(f"An error occurred: {e} while extracting transcript.")
        return None
    # Structurizing the Transcript
    api_key = os.environ['API_KEY_GEMINI']
    ai_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        'Content-Type': "applicaton/json",
        'x-goog-api-key': api_key
    }
    prompt = f"""
        Generate a well structured content with this transcript. Don't miss out any content.

        {full_transript}

        ["NOTE: Dont respond with intro or outro, only respond with the structured content."]
        ["NOTE: So that I can straightly store that in a variable by accessing your response using api."]
        """
    data = {
        'contents': [{'parts': [{'text': prompt}]}]
    }
    try:
        response = requests.post(ai_url , headers=headers, data=json.dumps(data))
        result = response.json()
        content_obj = result['candidates'][0]['content']['parts'][0]['text'] 
    except:
        print("Error Occured while content is extracted.")
        return None
    # Question Generator
    prompt = f"""
        Generate 10 multiple choice quiz questions based on the following text:

        "{str(content_obj)}"

        Format the output as a JSON array of objects, where each object contains:
        - "question": The quiz question.
        - "options": An array of answer options (for multiple_choice).
        - "correct_answer": The correct answer.
        """
    data = {
        'contents': [{'parts': [{'text': prompt}]}]
    }
    dictionary = {
        'summary': str(content_obj),
        'questions': []
    }
    try:
        response = requests.post(ai_url , headers=headers, data=json.dumps(data))
        result = response.json()
        question_obj = json.loads(result['candidates'][0]['content']['parts'][0]['text'].replace("\n", " ").replace("```json", "").replace("```", ""))
        questions = []
        for question in question_obj:
            availables= ['optionA','optionB','optionC','optionD' ]
            quest = {
                'question': question['question'],
            }
            i=0
            for option in availables:
                quest[option] = question['options'][i]
                i+=1
            quest['correct'] = question['correct_answer']
            questions.append(quest)
        dictionary['questions'] = questions
        return dictionary

    except:
        print("Error Occured...while Generating Questions")
        return None
    
def summary_extract(video_id):
    """Return the list of dictionary which represents questions."""
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id, languages=['en'])
    try:
        transcript = ytt_api.fetch(video_id, languages=['en'])
        full_transript = ""
        for segment in transcript:
            full_transript += (segment.text + " ")
    except Exception as e:
        print(f"An error occurred: {e} while extracting transcript.")
        return None

    api_key = 'AIzaSyCwAek2xvYYHrU4HM_-C8K9I2-CuMxL5Ts'
    ai_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        'Content-Type': "application/json",
        'x-goog-api-key': api_key
    }
    
    # Combined prompt
    prompt = f"""
    Summarise this Transcript.
    Video ID : {full_transript}
    Format the output as a string that contains only the summary:
    """
    data = {
        'contents': [{'parts': [{'text': prompt}]}]
    }

    try:
        response = requests.post(ai_url, headers=headers, data=json.dumps(data))
        result = response.json()
        
        summary = result['candidates'][0]['content']['parts'][0]['text']
        return summary

    except Exception as e:
        print(f"Error Occurred while generating questions: {e}")
        return None

    

