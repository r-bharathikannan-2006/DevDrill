from youtube_transcript_api import YouTubeTranscriptApi

video_id = 'xTtL8E4LzTQ'
ytt_api = YouTubeTranscriptApi()
try:
    transcript = ytt_api.fetch(video_id, languages=['en'])
    full_transcript = " ".join([segment.text for segment in transcript])
    print(full_transcript)
except Exception as e:
    print(f"An error occurred: {e} while extracting transcript.")