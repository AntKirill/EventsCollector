#!/usr/bin/python3
import logging
import shlex
import signal
import socketserver
import sys
import time
import urllib.request
from multiprocessing import Process

import humanfriendly

import server_api as api
import settings
import state_tracker
from EventsCollector import EventsCollector
from appindicator import indicator_main


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


def gc_to_trello():
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


def trello_to_gc():
    events_collector_instance = EventsCollector()
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


class MyTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.data = self.rfile.readline().strip()
        # print("{} wrote:".format(self.client_address[0]))
        query = shlex.split(self.data.decode("utf-8"))
        parsed_query = api.parse_arguments(query)
        q = parsed_query.query
        logging.info('Have new query: {0}'.format(q))
        if q == 'synch':
            if settings.DEBUG:
                print(q)
                return
            gc_to_trello()
            trello_to_gc()
        elif q == 'trello_to_gc':
            if settings.DEBUG:
                print(q)
                return
            trello_to_gc()
        elif q == 'gc_to_trello':
            if settings.DEBUG:
                print(q)
                return
            gc_to_trello()
        elif q == 'server_shutdown':
            self.server.need_shutdown = True


def run_ec_server():
    HOST, PORT = "localhost", 9999

    # Create the server, binding to host HOST on port PORT
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

    def signal_handler(sig, frame):
        logging.info('signal {0} caught on frame {1}, stop server'.format(sig, frame))
        server.server_close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    server.need_shutdown = False

    while not server.need_shutdown:
        server.handle_request()


def main():
    init_logger(settings.LOG_FILENAME)
    p = Process(target=run_ec_server)
    q = Process(target=indicator_main)
    p.start()
    q.start()
    p.join()
    q.join()
    # run_ec_server()


if __name__ == '__main__':
    main()
