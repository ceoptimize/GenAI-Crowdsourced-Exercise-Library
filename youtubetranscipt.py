from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime

#srt = YouTubeTranscriptApi.get_transcript(video_id)

videoListName = "videoidlists/list1.txt"
with open(videoListName) as f:
    video_ids = f.read().splitlines()

transcript_list, unretrievable_videos = YouTubeTranscriptApi.get_transcripts(video_ids, continue_after_error=True)

for video_id in video_ids:

    if video_id in transcript_list.keys():

        print("\nvideo_id = ", video_id)
        #print(transcript)

        srt = transcript_list.get(video_id)
        print(srt)

        text_list = []
        for i in srt:
            text_list.append(i['text'])

        text = ' '.join(text_list)
        print(text)
    
      #  print(text)