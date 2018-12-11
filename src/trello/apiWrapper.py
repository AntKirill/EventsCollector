import json
import logging

import requests
import webbrowser
# https://trello.com/1/authorize?expiration=1day&name=MyPersonalToken&scope=read&response_type=token&key=3e85bdd137af7678f0572a8f45b864b5&callback_method=fragment&return_url=https://google.com
from pip._vendor.distlib.compat import raw_input


def authenticate():
    global key, token, authPart
    cred_filename = "trello/credentials.json"
    with open(cred_filename, 'r') as file:
        credentials = json.load(file)
    key = credentials['api_key']
    token = credentials.get('secret_token')
    if token is None:
        webbrowser.open_new_tab("https://trello.com/1/authorize?expiration=1day&name=EventsCollector&scope=read,write&response_type=token&key=3e85bdd137af7678f0572a8f45b864b5")
        token = raw_input('Paste the token here: ')
        credentials['secret_token'] = token
        with open(cred_filename, 'w') as file:
            json.dump(credentials, file)

    authPart = {'key': key, 'token': token}

# Return list with all cards
def getAllCardsFromBoard(board_id_str):
    url = "https://api.trello.com/1/boards/" + board_id_str + "/cards"
    logging.info("performing HTTP query to get all cards from board with id {0}".format(board_id_str))
    resp = requests.request("GET", url, params=authPart)
    if resp.status_code == 200:
        logging.info("OK")
        return resp.json()
    return None


# Returns lists with all boards ids
def getAllBoardsIds():
    url = "https://api.trello.com/1/members/me/"
    logging.info("performing http query to get all boards")
    resp = requests.request("GET", url, params=authPart)
    if resp.status_code == 200:
        logging.info('OK')
        dict = resp.json()
        return dict['idBoards']
    return None


def getJsonBoardById(boardIdStr):
    url = "https://api.trello.com/1/boards/"
    url += boardIdStr
    logging.info("performing http query to get board with id {0}".format(boardIdStr))
    resp = requests.request("GET", url, params=authPart)
    if resp.status_code != 200:
        logging.info('loading table with id {0} failed'.format(boardIdStr))
        return None
    else:
        logging.info('OK')
        return resp.json()


def getBoardIdByName(boardsIdsList, name):
    if (boardsIdsList is None):
        return None
    logging.info('Iteration over all passed boardsIds to find board with name {0}'.format(name))
    for id in boardsIdsList:
        board = getJsonBoardById(id)
        if board is not None:
            if board['name'] == name:
                logging.info('Found')
                return board['id']
    logging.info('Not found')
    return None


def getAllListsOnBoard(boardIdStr):
    if (boardIdStr is None):
        return None
    url = 'https://api.trello.com/1/boards/'
    url += boardIdStr
    url += '/lists'
    logging.info("performing http query to get all lists from board with id {0}".format(boardIdStr))
    resp = requests.request("GET", url, params=authPart)
    if resp.status_code != 200:
        logging.info('FAILED!')
        return None
    else:
        logging.info('OK')
        return resp.json()


def getListIdByName(listsList, name):
    if (listsList is None):
        return None
    logging.info('Iterating over all passed lists to find list with name {0}'.format(name))
    for list in listsList:
        if list['name'] == name:
            logging.info('Found')
            return list['id']
    logging.info('Not found')
    return None


def postCardToList(listId, cardName, cardDescr=None):
    if (listId is None) or (cardName is None):
        return
    url = "https://api.trello.com/1/cards"
    params = {"name": cardName, "idList": listId, "keepFromSource": "all"}
    if cardDescr is not None:
        params['desc'] = cardDescr
    params.update(authPart)
    logging.info('Posting card to list with id {0}'.format(listId))
    resp = requests.request("POST", url, params=params)
    if resp.status_code != 200:
        logging.info('FAILED!')
    else:
        logging.info('OK')
