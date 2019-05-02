import datetime
import logging

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client, tools

import settings

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'


class GoogleCalendarClient:
    @staticmethod
    def do_authentication_flow(store):
        flow = client.flow_from_clientsecrets(settings.CREDENTIALS_FILE['google_calendar'], SCOPES)
        creds = tools.run_flow(flow, store)
        logging.getLogger().setLevel(getattr(logging, logging.getLevelName(logging.INFO)))
        return creds

    def do_authenticate(self, creds):
        self.service = build('calendar', 'v3', http=creds.authorize(Http()))
        return self.service

    def get_todays_allday_events(self, calendarId, timeMin, timeMax, singleEvents):
        eventsForTodayRes = self.service.events().list(calendarId=calendarId, timeMin=timeMin,
                                                       timeMax=timeMax, singleEvents=singleEvents).execute()
        return eventsForTodayRes.get('items', None)

    def get_all_calendars_ids(self):
        page_token = None
        items = []
        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                items.append(calendar_list_entry)
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        return items

    def get_upcoming_events(self, calendarId, amount):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(calendarId=calendarId, timeMin=now,
                                                   maxResults=amount, singleEvents=True,
                                                   orderBy='startTime').execute()

        return events_result.get('items', [])

    def post_event(self, event, calendar_id='primary'):
        resp = self.service.events().insert(calendarId=calendar_id, body=event).execute()
        return resp.get("error")
