import json
import logging


class TrelloManager:
    def __init__(self, client):
        self.client = client

    def authenticate(self):
        cred_filename = "trello/credentials.json"
        token_filename = "trello/token.json"
        with open(cred_filename, 'r') as file:
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
    def getAllCardsFromBoard(self, board_id_str):
        resp, status_code = self.client.get_all_cards_from_board(board_id_str)
        if status_code == 200:
            return resp
        return None

    # Returns lists with all boards ids
    def getAllBoardsIds(self):
        resp, status_code = self.client.get_all_boards_ids()
        if status_code == 200:
            return resp
        return None

    def getBoardById(self, boardIdStr):
        resp, status_code = self.client.get_board_by_id(boardIdStr)
        if status_code != 200:
            logging.info('loading table with id {0} failed'.format(boardIdStr))
            return None
        else:
            return resp

    def getBoardIdByName(self, boardsIdsList, name):
        if (boardsIdsList is None):
            return None
        logging.info('Iteration over all passed boardsIds to find board with name {0}'.format(name))
        for id in boardsIdsList:
            board = self.getBoardById(id)
            if board is not None:
                if board['name'] == name:
                    logging.info('Found')
                    return board['id']
        logging.info('Not found')
        return None

    def getAllListsOnBoard(self, boardIdStr):
        if (boardIdStr is None):
            return None
        resp, status_code = self.client.get_all_lists_from_board(boardIdStr)
        if status_code != 200:
            return None
        else:
            return resp

    def getListIdByName(self, listsList, name):
        if (listsList is None):
            return None
        logging.info('Iterating over all passed lists to find list with name {0}'.format(name))
        for list in listsList:
            if list['name'] == name:
                logging.info('Found')
                return list['id']
        logging.info('Not found')
        return None

    def postCardToList(self, listId, cardName, cardDescr=None):
        if (listId is None) or (cardName is None):
            logging.info("Invalid card, list id: {0}, card name: {1}. Skip it.".format(listId, cardName))
            return
        self.client.post_to_list(listId, cardName, cardDescr)
