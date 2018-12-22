import json
import logging

import settings


class TrelloManager:
    def __init__(self, client):
        self.client = client

    def authenticate(self):
        cred_file = settings.CREDENTIALS_FILE['trello']  # TODO: Refactor this. Make simular interface.
        token_filename = "trello/token.json"
        with cred_file.open(mode='r') as file:
            credentials_json = json.load(file)
        key = credentials_json['api_key']
        try:
            with open(token_filename, 'r') as file:
                token_json = json.load(file)
            token = token_json.get('secret_token')
        except FileNotFoundError:
            token = self.client.do_authentication_flow(key)
            with open(token_filename, 'w') as file:
                json.dump({"secret_token": token}, file)
        self.client.do_authenticate(key, token)

    # Return list with all cards
    def get_all_cards_from_board(self, board_id_str):
        resp, status_code = self.client.get_all_cards_from_board(board_id_str)
        if status_code == 200:
            return resp
        return None

    # Returns lists with all boards ids
    def get_all_boards_ids(self):
        resp, status_code = self.client.get_all_boards_ids()
        if status_code == 200:
            return resp
        return None

    def get_board_by_id(self, board_id_str):
        resp, status_code = self.client.get_board_by_id(board_id_str)
        if status_code != 200:
            logging.info('loading table with id {0} failed'.format(board_id_str))
            return None
        else:
            return resp

    def get_board_id_by_name(self, boards_ids_list, name):
        if (boards_ids_list is None):
            return None
        logging.info('Iteration over all passed boardsIds to find board with name {0}'.format(name))
        for id in boards_ids_list:
            board = self.get_board_by_id(id)
            if board is not None:
                if board['name'] == name:
                    logging.info('Found')
                    return board['id']
        logging.info('Not found')
        return None

    def get_all_lists_on_board(self, board_id_str):
        if board_id_str is None:
            return None
        resp, status_code = self.client.get_all_lists_from_board(board_id_str)
        if status_code != 200:
            return None
        else:
            return resp

    @staticmethod
    def get_list_id_by_name(lists_list, name):
        if lists_list is None:
            return None
        logging.info('Iterating over all passed lists to find list with name {0}'.format(name))
        for list in lists_list:
            if list['name'] == name:
                logging.info('Found')
                return list['id']
        logging.info('Not found')
        return None

    def post_card_to_list(self, list_id, card_name, card_descr=None):
        if (list_id is None) or (card_name is None):
            logging.info("Invalid card, list id: {0}, card name: {1}. Skip it.".format(list_id, card_name))
            return
        self.client.post_to_list(list_id, card_name, card_descr)
