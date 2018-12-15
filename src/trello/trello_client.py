import logging
import webbrowser

import requests
from pip._vendor.distlib.compat import raw_input

# If modifying these scopes, delete the file token.json.
SCOPES = "https://trello.com/1/authorize?expiration=never&name=EventsCollector&scope=read,write&response_type=token&key="


class TrelloClient:
    @staticmethod
    def do_authentication_flow(api_key):
        request_url = SCOPES
        request_url += api_key
        webbrowser.open_new_tab(request_url)
        return raw_input('Paste the token here: ')

    def do_authenticate(self, api_key, secret_token):
        self.authPart = {"key": api_key, "token": secret_token}

    def __do_query(self, url):
        resp = requests.request("GET", url, params=self.authPart)
        if resp.status_code == 200:
            logging.info("OK")
        else:
            logging.info("Failed GET request to {0}, status code: {1}".format(resp.url, resp.status_code))
        return resp.json(), resp.status_code

    def get_all_boards_ids(self):
        url = "https://api.trello.com/1/members/me/"
        logging.info("performing http query to get all boards")
        ids, status_code = self.__do_query(url)
        return ids['idBoards'], status_code

    def get_all_cards_from_board(self, board_id_str):
        url = "https://api.trello.com/1/boards/" + board_id_str + "/cards"
        logging.info("performing HTTP query to get all cards from board with id {0}".format(board_id_str))
        return self.__do_query(url)

    def get_board_by_id(self, board_id_str):
        url = "https://api.trello.com/1/boards/"
        url += board_id_str
        logging.info("performing http query to get board with id {0}".format(board_id_str))
        return self.__do_query(url)

    def get_all_lists_from_board(self, board_id_str):
        url = 'https://api.trello.com/1/boards/'
        url += board_id_str
        url += '/lists'
        logging.info("performing http query to get all lists from board with id {0}".format(board_id_str))
        return self.__do_query(url)

    def post_to_list(self, listId, cardName, cardDescr):
        url = "https://api.trello.com/1/cards"
        params = {"name": cardName, "idList": listId, "keepFromSource": "all"}
        if cardDescr is not None:
            params['desc'] = cardDescr
        params.update(self.authPart)
        logging.info('Posting card to list with id {0}'.format(listId))
        resp = requests.request("POST", url, params=params)
        if resp.status_code == 200:
            logging.info('OK')
        else:
            logging.info("Failed POST request to {0}, status code: {1}".format(resp.url, resp.status_code))
        return resp.json(), resp.status_code
