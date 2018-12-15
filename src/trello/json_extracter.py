# Return str date (like 2018-09-26) from card with due (like 2018-09-26T09:00:00.000Z)
def get_date_str_from_card(card_with_due):
    res = card_with_due['due'].split('T')
    return res.pop(0)


def is_card_with_deadline(card):
    return card.get('due') is None


# Return str time (like 09:00:00) from due (like 2018-09-26T09:00:00.000Z)
def get_time_str_from_card(card_with_due):
    return card_with_due['due'].split('T').pop(1).split('.').pop(0)


def get_name_str_from_card(card):
    return card['name']


def get_card_url(card):
    return card['url']
