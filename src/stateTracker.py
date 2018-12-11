import datetime
import json
import logging

import googleCalendar.jsonExtracter as je

file_name = 'state.json'


def load_state():
    logging.info('Try to load state from file {0}'.format(file_name))
    try:
        with open(file_name, 'r') as file:
            dict = json.load(file)
            logging.info('Loaded')
            return dict
    except FileNotFoundError:
        logging.info('File {0} not found'.format(file_name))
        return {}
    except TypeError as e:
        logging.info('Bad json file, so rewrite it. Error msg: {0}'.format(str(e)))
        return {}


def _hash_board_and_list_name(board_name, list_name):
    return board_name + '$' + list_name


def save_list_id(state, board_name, list_name, list_id):
    hashed_name = _hash_board_and_list_name(board_name, list_name)
    state[hashed_name] = list_id


def get_hashed_list_id(state, board_name, list_name):
    hashed_name = _hash_board_and_list_name(board_name, list_name)
    return state.get(hashed_name)


def get_new_events(state, gc_events):
    logging.info('Searching for new events')

    state_date_dict = state.get('__date__')

    # Check date
    if state_date_dict is not None:
        that_date = datetime.datetime(int(state_date_dict['year']), int(state_date_dict['month']),
                                      int(state_date_dict['day']))
        cur_date = datetime.datetime.today()
        if that_date.date() != cur_date.date():
            logging.info('Old date: {0}'.format(that_date.date()))
            logging.info('Cur date: {0}'.format(cur_date.date()))
            logging.info('New date so clear old state')
            state.clear()
        else:
            logging.info('The same date')
    else:
        logging.info('No date found')

    # Look for new events
    new_events_list = []
    if gc_events is None:
        return new_events_list
    for e in gc_events:
        gc_event_name = je.getEventName(e)
        _mapped = state.get(gc_event_name)
        if _mapped is None:
            logging.info('New event: {0} found '.format(gc_event_name))
            new_events_list.append(e)
    return new_events_list


def update_state(old_state, new_events_list):
    logging.info('Updating state')

    # Update date
    cur_date = datetime.datetime.today()
    old_state['__date__'] = {'year': str(cur_date.year), 'month': str(cur_date.month), 'day': str(cur_date.day)}

    # Update events
    for ne in new_events_list:
        old_state[je.getEventName(ne)] = 'True'
    with open(file_name, 'w') as file:
        json.dump(old_state, file)
    return old_state
