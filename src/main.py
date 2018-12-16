import logging
import os
import time
import urllib.request

import humanfriendly

import changes_watcher
from EventsCollector import EventsCollector
import settings
import state_tracker


def wait_for_internet_connection():
    logging.info('Waiting for network ...')
    while True:
        try:
            urllib.request.urlopen('http://google.com')
            logging.info('Got network connection')
            return
        except urllib.request.URLError:
            time.sleep(1)
            pass


def pull_events():
    wait_for_internet_connection()
    events_collector_instance = EventsCollector()
    events = events_collector_instance.get_today_allday_events_from_google_calendar()
    cur_state = state_tracker.load_state()
    new_events = state_tracker.get_new_events(cur_state, events)
    if len(new_events) is 0:
        logging.info("No new events, so return")
    else:
        logging.info('Posting to trello.com')
        events_collector_instance.post_to_trello(cur_state, "My To Do Board", "Incoming", new_events)
        state_tracker.update_state(cur_state, new_events)
    events_collector_instance.shift_deadlines_from_trello_to_google_calendar("My To Do Board")


def init_logger(log_filename, max_size='1Mb'):
    log_dir = settings.ROOT_DIRECTORY / 'log'
    log_dir.mkdir(parents=True, exist_ok=True)  # Created directory with the default permissions

    log_file = log_dir / log_filename

    # Clear log file if its size more than max_size
    if log_file.exists():
        if log_file.stat().st_size > humanfriendly.parse_size(max_size, binary=True):
            log_file.open(mode='w').close()
    else:
        log_file.open(mode='w').close()


    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=log_file.resolve().as_posix(), level=logging.INFO, format=log_format)


def main():
    init_logger(settings.LOG_FILENAME)

    changes_watcher.watch_modify("./invokefiles/", pull_events) # blocking call
    # pull_events()  # TODO: Run in loop with timeout


if __name__ == '__main__':
    main()
