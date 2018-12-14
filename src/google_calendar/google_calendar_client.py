import datetime
import logging

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client, tools

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'


class GoogleCalendarClient():
    def do_authentication_flow(self, store):
        flow = client.flow_from_clientsecrets('google_calendar/credentials.json', SCOPES)
        return tools.run_flow(flow, store)

    def do_authenticate(self, creds):
        self.service = build('calendar', 'v3', http=creds.authorize(Http()))
        return self.service

    def get_todays_allday_events(self, calendarId, timeMin, timeMax, singleEvents):
        eventsForTodayRes = self.service.events().list(calendarId=calendarId, timeMin=timeMin,
                                          timeMax=timeMax, singleEvents=singleEvents).execute()
        return eventsForTodayRes.get('items', None)

    def get_upcoming_events(self, calendarId, amount):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(calendarId=calendarId, timeMin=now,
                                          maxResults=amount, singleEvents=True,
                                          orderBy='startTime').execute()

        return events_result.get('items', [])

    def post_event(self, event):
        resp = self.service.events().insert(calendarId='primary', body=event).execute()
        return resp.get("error")
