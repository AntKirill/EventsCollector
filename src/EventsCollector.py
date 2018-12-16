import logging

import google_calendar.google_calendar_client as google_calendar_client
import google_calendar.google_calendar_manager as google_calendar_api
import google_calendar.json_extracter as gc_json_extracter
import state_tracker


import trello.json_extracter as trello_json_extracter
import trello.trello_client as trello_client
import trello.trello_manager as trello_api


class EventsCollector:
    def __init__(self):
        self.google_calendar_manager = google_calendar_api.GoogleCalendarManager(
            google_calendar_client.GoogleCalendarClient())
        self.google_calendar_manager.authenticate()
        self.trello_manager = trello_api.TrelloManager(trello_client.TrelloClient())
        self.trello_manager.authenticate()

    def post_to_trello(self, state, board_name, list_name, events_list):
        logging.info('Start posting to list {1} of board {0}'.format(board_name, list_name))
        if len(events_list) is 0:
            logging.info('Empty events list, so return')
            return

        logging.info('Try to guess target list id')
        list_id_guess = state_tracker.get_hashed_list_id(state, board_name, list_name)

        if list_id_guess is None:
            logging.info('No guess')
            board_ids_list = self.trello_manager.getAllBoardsIds()
            board_id = self.trello_manager.getBoardIdByName(board_ids_list, board_name)
            lists_list = self.trello_manager.getAllListsOnBoard(board_id)
            incoming_list_id = self.trello_manager.getListIdByName(lists_list, list_name)
            state_tracker.save_list_id(state, board_name, list_name, incoming_list_id)
        else:
            logging.info('Guessed id is {0}'.format(list_id_guess))
            incoming_list_id = list_id_guess
        for event in events_list:
            logging.info('posting card with name {0}'.format(gc_json_extracter.getEventName(event)))
            self.trello_manager.postCardToList(incoming_list_id, gc_json_extracter.getEventName(event),
                                               gc_json_extracter.getDescription(event))

    def get_today_allday_events_from_google_calendar(self):
        logging.info('Get todays all-day events from google calendar')
        allDaysList = self.google_calendar_manager.get_todays_all_day_events()
        logging.info('Done')
        return allDaysList

    def shift_deadlines_from_trello_to_google_calendar(self, board_name):
        def mangle_name_for_gc(name):
            return "Дедлайн по: " + name

        def demangle_name_for_gc(mangled_name):
            pref = "Дедлайн по: "
            pref_len = len(pref)
            suf_len = len(name_to_card_gc) - pref_len
            if mangled_name[:suf_len] == pref:
                return mangled_name[pref_len:]

        logging.info("Shifting all deadlines from trello.com to google calendar")
        board_ids_list = self.trello_manager.getAllBoardsIds()
        my_board_id = self.trello_manager.getBoardIdByName(board_ids_list, board_name)

        # Get all cards with deadlines from main board of Trello.com

        trello_cards_list = self.trello_manager.getAllCardsFromBoard(my_board_id)
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
            card_gc_list = self.google_calendar_manager.get_all_day_events(date)
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
                self.google_calendar_manager.post_event(mangle_name_for_gc(card_name), date_str=card_date,
                                                        color_id_str="11",
                                                        event_description_str=card_url)
                # Create event at current time
                # card_time = trello_json_extracter.get_time_str_from_card(card)
                # gc.postEvent(service, card_name, date_str=card_date, time_str=card_time, color_id_str="11")

        logging.info("Shifting done")
