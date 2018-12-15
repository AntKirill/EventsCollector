def getStartDate(e):
    return e.get('start').get('date')


def getDateTime(e):
    return e.get('start').get('dateTime')


def getStart(e):
    return e.get('start')


def getEventName(e):
    return e.get('summary')


def getDescription(e):
    return e.get('description')
