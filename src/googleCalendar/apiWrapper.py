import datetime
import json
import logging
import time

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'


# Returns google api service
def authenticate():
    store = file.Storage('googleCalendar/token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('googleCalendar/credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    return service


# Returns dictionary of json object with N upcoming events
def getNUpcomingEvents(service, eventsAmount):
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    logging.info('Getting the upcoming {0} events'.format(eventsAmount))
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=eventsAmount, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        logging.info('No upcoming events found.')
        return None
    return events


def getAllDayEvents(service, date_iso):
    t = time.strptime(date_iso, "%Y-%m-%d")
    day = datetime.date(t.tm_year, t.tm_mon, t.tm_mday)

    startDayTimeStr = day.isoformat()
    startDayTimeStr += 'T00:00:00Z'
    endDayTimeStr = day.isoformat()
    endDayTimeStr += 'T00:01:00Z'
    eventsForTodayRes = service.events().list(calendarId='primary', timeMin=startDayTimeStr,
                                              timeMax=endDayTimeStr, singleEvents=True).execute()
    eventsForToday = eventsForTodayRes.get('items', None)
    allDays = []
    if eventsForToday is not None:
        for event in eventsForToday:
            if event['start'].get('dateTime') is None:
                allDays.append(event)
    return allDays


# Returns list with all all-day events for today
def getTodaysAllDayEvents(service):
    return getAllDayEvents(service, datetime.date.today().isoformat())


# Return None with ok and error_str if not
def postEvent(service, event_name_str, date_str, time_str=None, color_id_str=None, event_description_str=None):
    if time_str is not None:
        t = time.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M:%S")
    else:
        t = time.strptime(date_str, "%Y-%m-%d")
    end_date_str = datetime.date(t.tm_year, t.tm_mon, t.tm_mday)
    end_date_str += datetime.timedelta(days=1)

    # Configuring event
    if time_str is None:
        start = {"date": date_str}
        end = {"date": end_date_str.isoformat()}
    else:
        start = {"dateTime": date_str + "T" + time_str, "timeZone": "Europe/Moscow"}
        end = {"dateTime": date_str + "T" + datetime.time(t.tm_hour + 1, t.tm_min, t.tm_sec).isoformat(),
               "timeZone": "Europe/Moscow"}

    logging.info("start: " + json.dumps(start))
    logging.info("end: " + json.dumps(end))

    body = {
        "end": end,
        "start": start,
        "summary": event_name_str,
        "reminders": {
            "overrides": "",
            "useDefault": "false"
        }
    }
    if event_description_str is not None:
        body["description"] = event_description_str
    if color_id_str is not None:
        body['colorId'] = color_id_str

    logging.info("Posting event with name {0} to google calendar".format(event_name_str))
    resp = service.events().insert(calendarId='primary', body=body).execute()
    logging.info("Done")
    return resp.get('error')
