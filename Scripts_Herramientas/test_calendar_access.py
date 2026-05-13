import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

TOKEN_PATHS = [
    'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json',
    'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token.json'
]

def check_calendar_access():
    print("Checking Google Calendar access...")
    for path in TOKEN_PATHS:
        if not os.path.exists(path):
            continue
            
        print(f"\nTrying token: {os.path.basename(path)}")
        try:
            with open(path, 'r') as f:
                token_data = json.load(f)
                scopes = token_data.get('scopes', [])
                print(f"Scopes found: {scopes}")
            
            creds = Credentials.from_authorized_user_file(path)
            service = build('calendar', 'v3', credentials=creds)
            
            now = datetime.utcnow().isoformat() + 'Z'
            print('Getting today\'s events...')
            events_result = service.events().list(calendarId='primary', timeMin=now,
                                                maxResults=10, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')
            else:
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    print(start, event['summary'])
            
            print("✅ SUCCESS: Calendar access granted!")
            return True
            
        except HttpError as error:
            print(f'API Error: {error}')
        except Exception as e:
            print(f'Error with {path}: {e}')
            
    return False

if __name__ == "__main__":
    check_calendar_access()
