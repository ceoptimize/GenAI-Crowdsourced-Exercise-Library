from googleapiclient.discovery import build
import re

def convert_string_to_int(string_var):
    try:
        # Try to convert the string to an integer
        int_var = int(string_var)
        return int_var
    except ValueError:
        # If the string is not a number, set the integer variable to 0
        int_var = 0
        return int_var

# Replace with your own API key
API_KEY = 'AIzaSyBc9qycvVaBAeG9DV8KewsLKGnmVyBUkgk'

# Replace with your own search query
search_query = 'intitle:"Landmine Lateral Raise"'
channel_ids = ['UCpyjZrR0so-aHFIyg2U0cyw', 'UCXrWnUUIza2gpaXhVknC55Q']
channel_id = 'UCpyjZrR0so-aHFIyg2U0cyw'
# Build the YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)


search_params = {
    'q': search_query,
    'part': 'id', 'snippet',
    'type': 'video',
    'maxResults': 50,
    'videoDuration' = 'short'
}

# Set the video duration to "short" and retrieve up to 50 videos
search_response = youtube.search().list(
    q=search_query,
    type='video',
    videoDuration='short',
    maxResults=50,
    part='id,snippet',
    channelId = channel_id
).execute()

# Filter the search results to only include videos that are less than 60 seconds long
filtered_results = []
pattern = "(?<=PT)(?P<minutes>\d*M)*(?P<seconds>\d*S)*"

for channel_id in channel_ids:
    search_params['channelId'] = channel_id
    search_response = youtube.search().list(**search_params).execute()

    # Print the video titles for the search results
    for search_result in search_response.get('items', []):
        print(search_result['snippet']['title'])
for search_result in search_response.get('items', []):
    video_id = search_result['id']['videoId']
    video_response = youtube.videos().list(
        id=video_id,
        part='contentDetails'
    ).execute()
    duration = video_response['items'][0]['contentDetails']['duration']
    #print(re.split())
    #print(duration)
    timegroups = re.findall(pattern,duration)
    minutes = convert_string_to_int(re.split('M', timegroups[0][0])[0])
    #print(minutes)
    seconds = convert_string_to_int(re.split('S', timegroups[0][1])[0])
    #print(seconds)
    totaltime = minutes*60+seconds
    if (totaltime < 40) & (totaltime > 10):
        filtered_results.append(search_result)
   # print(duration.split('S')[0])
   # if 'S' in duration:
  #      filtered_results.append(search_result)

   # if 'S' in duration and int(duration.split('S')[0]) < 60:
       # filtered_results.append(search_result)

# Print the filtered search results
for search_result in filtered_results:
    print(search_result['id'])
    print(search_result['snippet']['title'])
