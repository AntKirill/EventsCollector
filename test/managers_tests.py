from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

import src.google_calendar.google_calendar_manager as google_calendar_manager


class TestGoogleCalendarManager(TestCase):

    def setUp(self):
        self.x = 0

    def __side_function(self, a):
        self.x += 1

    @patch('src.google_calendar.google_calendar_client.GoogleCalendarClient')
    def test_authenticate_no_token(self, MockClient):
        client = MockClient()

        client.do_authentication_flow.side_effect = self.__side_function
        client.do_authenticate.return_value = "hello"

        manager = google_calendar_manager.GoogleCalendarManager(client)
        str = manager.authenticate()
        self.assertEqual(str, 'hello')
        self.assertEqual(self.x, 1)

    @patch('src.google_calendar.google_calendar_client.GoogleCalendarClient')
    def test_authenticate_with_token(self, MockClient):
        client = MockClient()

        import os
        if not os.path.exists("google_calendar"):
            os.makedirs("google_calendar")
        with open("google_calendar/token.json", "w") as file:
            file.close()

        client.do_authentication_flow.return_value = self.__side_function
        client.do_authenticate.return_value = "hello"

        manager = google_calendar_manager.GoogleCalendarManager(client)
        str = manager.authenticate()
        os.remove("google_calendar/token.json")
        os.removedirs("google_calendar")
        self.assertEqual(str, 'hello')
        self.assertEqual(self.x, 0)

    @patch('src.google_calendar.google_calendar_client.GoogleCalendarClient')
    def test_get_n_upcoming_events(self, MockClient):
        client = MockClient()

        client.get_upcoming_events.return_value = []
        manager = google_calendar_manager.GoogleCalendarManager(client)
        self.assertEqual(manager.get_n_upcoming_events(10), None)

        client.get_upcoming_events.return_value = {"abc": "cba"}
        manager = google_calendar_manager.GoogleCalendarManager(client)
        self.assertEqual(manager.get_n_upcoming_events(1), {"abc": "cba"})

    @patch('src.google_calendar.google_calendar_client.GoogleCalendarClient')
    def test_get_all_day_events(self, MockClient):
        client = MockClient()

        client.get_todays_allday_events.return_value = None
        manager = google_calendar_manager.GoogleCalendarManager(client)
        self.assertEqual(manager.get_all_day_events("2018-09-06"), [])

        client.get_todays_allday_events.return_value = [
            {"start": {"dateTime": "hello"}, "stop": {"dateTime": "goodbay"}}]
        manager = google_calendar_manager.GoogleCalendarManager(client)
        self.assertEqual(manager.get_all_day_events("2018-10-13"), [])

        events_list1 = [
            {"start": {"1": "2"}}, {"start": {"start": "start"}}, {"start": {"2": "3"}, "stop": "hello"}
        ]
        client.get_todays_allday_events.return_value = events_list1
        manager = google_calendar_manager.GoogleCalendarManager(client)
        self.assertEqual(manager.get_all_day_events("2018-01-01"), events_list1)

        events_list2 = [
            {"start": {"1": "2"}}, {"start": {"start": "start"}},
            {"start": {"dateTime": "goodbay"}, "end": {"stop": "finish"}}, {"start": {"2": "3"}, "stop": "hello"}
        ]
        client.get_todays_allday_events.return_value = events_list2
        manager = google_calendar_manager.GoogleCalendarManager(client)
        self.assertEqual(manager.get_all_day_events("2018-02-10"), events_list1)

    @patch('src.google_calendar.google_calendar_client.GoogleCalendarClient')
    def test_get_todays_all_day_events(self, MockClient):
        client = MockClient()

        client.get_todays_allday_events.return_value = None
        manager = google_calendar_manager.GoogleCalendarManager(client)
        self.assertEqual(manager.get_todays_all_day_events(), [])

    @patch('src.google_calendar.google_calendar_client.GoogleCalendarClient')
    def test_post_event(self, MockClient):
        client = MockClient()

        client.post_event.side_effect = self.__gc_event_paramets_validator__
        manager = google_calendar_manager.GoogleCalendarManager(client)
        manager.post_event("hello_world", "2018-09-10")
        manager.post_event("hello_world", "2018-12-31")
        manager.post_event("hello_world", "2018-01-01", "10:00:00")
        manager.post_event("hello_world", "2018-11-30", "22:59:59")

    def __gc_event_paramets_validator__(self, event):
        start = event.get("start")
        self.assertIsNotNone(start)
        end = event.get('end')
        self.assertIsNotNone(end)
        start_date_time = start.get("dateTime")
        if start_date_time is None:
            date_format = "%Y-%m-%d"
            start_date = start.get('date')
            self.assertIsNotNone(start_date)
            end_date = end.get('date')
            self.assertIsNotNone(end_date)
            try:
                start_date_iso = datetime.strptime(start_date, date_format)
                end_date_iso = datetime.strptime(end_date, date_format)
            except ValueError:
                self.fail("strptime raised ValueError unexpectedly!")
            delta = end_date_iso - start_date_iso
            self.assertEqual(delta.days, 1)
        else:
            date_time_format = "%Y-%m-%dT%H:%M:%S"
            end_date_time = end.get('dateTime')
            self.assertIsNotNone(end_date_time)
            try:
                start_date_time_iso = datetime.strptime(start_date_time, date_time_format)
                end_date_time_iso = datetime.strptime(end_date_time, date_time_format)
            except:
                self.fail("strptime raised ValueError unexpectedly!")
            delta = end_date_time_iso - start_date_time_iso
            self.assertEqual(delta.seconds, 3600)
