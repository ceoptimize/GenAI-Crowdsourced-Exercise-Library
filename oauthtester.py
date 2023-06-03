import json
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


class YouTubeOAuthTester:
    def __init__(self, client_secrets_file):
        self.client_secrets_file = client_secrets_file
        self.scopes = ['https://www.googleapis.com/auth/youtube.readonly']
        self.api_service_name = 'youtube'
        self.api_version = 'v3'
        self.client = None

    def authenticate(self):
        # Load client secrets from the JSON file
        with open(self.client_secrets_file) as file:
            client_secrets = json.load(file)

        # Create credentials flow from client secrets
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, self.scopes)

        # Run the OAuth flow and obtain credentials
        credentials = flow.run_local_server(port=8080)

        # Build the YouTube API client
        self.client = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=credentials)

    def test_api(self):
        try:
            # Make a test request to the YouTube API
            request = self.client.channels().list(
                part='snippet',
                mine=True
            )
            response = request.execute()

            if 'items' in response:
                print('API request successful!')
                channel_title = response['items'][0]['snippet']['title']
                print('Channel Title:', channel_title)
            else:
                print('No channels found.')
        except googleapiclient.errors.HttpError as e:
            print(f'API request failed with error: {e}')


# Usage example
secrets_file = 'client_secrets3.json'  # Replace with your client secrets file name

# Check if the secrets file exists
if os.path.exists(secrets_file):
    tester = YouTubeOAuthTester(secrets_file)
    tester.authenticate()
    tester.test_api()
else:
    print(f'Client secrets file "{secrets_file}" not found.')
