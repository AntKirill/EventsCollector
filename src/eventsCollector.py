import logging
import os
import time
import urllib.request

from pathlib import Path

import changesWatcher
import humanfriendly
import googleCalendar.apiWrapper as google_calendar_api
import googleCalendar.jsonExtracter as gc_json_extracter
import stateTracker as state_tracker
import trello.apiWrapper as trello_api
import trello.jsonExtracter as trello_json_extracter


def post_to_trello(state, board_name, list_name, events_list):
    logging.info('Start posting to list {1} of board {0}'.format(board_name, list_name))
    if len(events_list) is 0:
        logging.info('Empty events list, so return')
        return
    trello_api.authenticate()

    logging.info('Try to guess target list id')
    list_id_guess = state_tracker.get_hashed_list_id(state, board_name, list_name)

    if list_id_guess is None:
        logging.info('No guess')
        board_ids_list = trello_api.getAllBoardsIds()
        board_id = trello_api.getBoardIdByName(board_ids_list, board_name)
        lists_list = trello_api.getAllListsOnBoard(board_id)
        incoming_list_id = trello_api.getListIdByName(lists_list, list_name)
        state_tracker.save_list_id(state, board_name, list_name, incoming_list_id)
    else:
        logging.info('Guessed id is {0}'.format(list_id_guess))
        incoming_list_id = list_id_guess
    for event in events_list:
        logging.info('posting card with name {0}'.format(gc_json_extracter.getEventName(event)))
        trello_api.postCardToList(incoming_list_id, gc_json_extracter.getEventName(event),
                                  gc_json_extracter.getDescription(event))


def get_today_allday_events_from_google_calendar():
    logging.info('Get todays all-day events from google calendar')
    service = google_calendar_api.authenticate()
    allDaysList = google_calendar_api.getTodaysAllDayEvents(service)
    logging.info('Done')
    return allDaysList


def shift_deadlines_from_trello_to_google_calendar(board_name):
    def mangle_name_for_gc(name):
        return "Дедлайн по: " + name

    def demangle_name_for_gc(mangled_name):
        pref = "Дедлайн по: "
        pref_len = len(pref)
        suf_len = len(name_to_card_gc) - pref_len
        if mangled_name[:suf_len] == pref:
            return mangled_name[pref_len:]

    logging.info("Shifting all deadlines from trello.com to google calendar")
    trello_api.authenticate()
    service = google_calendar_api.authenticate()
    board_ids_list = trello_api.getAllBoardsIds()
    my_board_id = trello_api.getBoardIdByName(board_ids_list, board_name)

    # Get all cards with deadlines from main board of Trello.com

    trello_cards_list = trello_api.getAllCardsFromBoard(my_board_id)
    date_to_cards_list = {}
    for card in trello_cards_list:
        if trello_json_extracter.is_card_with_deadline(card) is False:
            date = trello_json_extracter.get_date_str_from_card(card)
            cards_list_that_date = date_to_cards_list.get(date)
            if cards_list_that_date is None:
                date_to_cards_list[date] = [card]
            else:
                cards_list_that_date.append(card)

    # Post all cards with deadlines to google calendar
    for date, cards_list in date_to_cards_list.items():
        card_gc_list = google_calendar_api.getAllDayEvents(service, date)
        name_to_card_gc = {}
        for card in card_gc_list:
            name = gc_json_extracter.getEventName(card)
            name_to_card_gc[name] = card

        for card in cards_list:
            card_name = trello_json_extracter.get_name_str_from_card(card)
            if name_to_card_gc.get(mangle_name_for_gc(card_name)) is not None:
                logging.info("already have event with name {0}, so skip it".format(card_name))
                continue
            card_date = trello_json_extracter.get_date_str_from_card(card)
            card_url = trello_json_extracter.get_card_url(card)
            # Create all-day red event
            google_calendar_api.postEvent(service, mangle_name_for_gc(card_name), date_str=card_date, color_id_str="11",
                                          event_description_str=card_url)
            # Create event at current time
            # card_time = trello_json_extracter.get_time_str_from_card(card)
            # gc.postEvent(service, card_name, date_str=card_date, time_str=card_time, color_id_str="11")

    logging.info("Shifting done")


def wait_for_internet_connection():
    while True:
        try:
            urllib.request.urlopen('http://google.com')
            logging.info('Got network connection')
            return
        except urllib.request.URLError:
            logging.info('Waiting for network ...')
            time.sleep(1)
            pass


def start_events_collector():
    wait_for_internet_connection()
    events = get_today_allday_events_from_google_calendar()
    cur_state = state_tracker.load_state()
    new_events = state_tracker.get_new_events(cur_state, events)
    if len(new_events) is 0:
        logging.info("No new events, so return")
    else:
        logging.info('Posting to trello.com')
        post_to_trello(cur_state, "My To Do Board", "Incoming", new_events)
        state_tracker.update_state(cur_state, new_events)
    shift_deadlines_from_trello_to_google_calendar("My To Do Board")


def init_logger(log_filename, max_size="1Mb"):
    root_dir = Path()  # TODO: Change later
    log_dir = root_dir / 'log'
    log_dir.mkdir(parents=True, exist_ok=True)  # Created with the default permissions

    log_file = log_dir / log_filename
    log_file.resolve()  # Optimize file path

    # Clear log file if its size more than max_size
    if log_file.exists():
        if log_file.stat().st_size > humanfriendly.parse_size(max_size, binary=True):
            log_file.open(mode='w').close()

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=log_file, level=logging.INFO, format=log_format)
    logging.info("No new events, so return")


def main():
    log_filename = 'eventsCollector.log'
    init_logger(log_filename)

    os.chdir("./src")  # TODO: Move "./invokeFiles/" and secret tokens and delete this
    # changesWatcher.watch_modify("./invokeFiles/", start_events_collector)  # blocking call # TODO: Uncomment this
    start_events_collector()


if __name__ == '__main__':
    main()
