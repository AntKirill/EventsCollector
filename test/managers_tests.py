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
