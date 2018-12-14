import datetime
import json
import logging
import time
from oauth2client import file


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'


class GoogleCalendarManager:

    def __init__(self, gc_client):
        self.client = gc_client

    # Returns google api service
    def authenticate(self):
        store = file.Storage('google_calendar/token.json')
        creds = store.get()
        if not creds or creds.invalid:
            creds = self.client.do_authentication_flow(store)
        return self.client.do_authenticate(creds)

    # Returns dictionary of json object with N upcoming events
    def getNUpcomingEvents(self, eventsAmount):
        logging.info('Getting the upcoming {0} events'.format(eventsAmount))
        events = self.client.get_upcoming_events('primary', eventsAmount)

        if not events:
            logging.info('No upcoming events found.')
            return None
        return events

    def getAllDayEvents(self, date_iso):
        t = time.strptime(date_iso, "%Y-%m-%d")
        day = datetime.date(t.tm_year, t.tm_mon, t.tm_mday)

        startDayTimeStr = day.isoformat()
        startDayTimeStr += 'T00:00:00Z'
        endDayTimeStr = day.isoformat()
        endDayTimeStr += 'T00:01:00Z'
        eventsForToday = self.client.get_todays_allday_events('primary', startDayTimeStr, endDayTimeStr, True)
        allDays = []
        if eventsForToday is not None:
            for event in eventsForToday:
                if event['start'].get('dateTime') is None:
                    allDays.append(event)
        return allDays

    # Returns list with all all-day events for today
    def getTodaysAllDayEvents(self):
        return self.getAllDayEvents(datetime.date.today().isoformat())

    # Return None with ok and error_str if not
    def postEvent(self, event_name_str, date_str, time_str=None, color_id_str=None, event_description_str=None):
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
        resp_error = self.client.post_event(body)
        logging.info("Done")
        return resp_error
