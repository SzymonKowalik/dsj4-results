from itertools import zip_longest


def read_planned_calendar():
    """Reads the planned_calendar.txt file and returns a list of planned competition names."""
    try:
        with open('./data/planned_calendar.txt', encoding='UTF-8') as file:
            return [line.rstrip() for line in file if not line.startswith('#') and line != '\n']
    except FileNotFoundError:
        open('./data/planned_calendar.txt', 'w')


def return_calendar(cursor):
    """
    Generates the calendar of planned and actual competitions.
    Returns:
        list: List of lists containing the ID and name of each competition and status"""
    planned_calendar = read_planned_calendar()
    cursor.execute('SELECT hill FROM competitions')
    actual_calendar = [hill[0] for hill in cursor.fetchall()]

    official_calendar = []
    for comp_id, calendar in enumerate(zip_longest(planned_calendar, actual_calendar), 1):
        planned, actual = calendar
        if actual is not None:
            official_calendar.append([comp_id, actual, 'completed'])
        else:
            official_calendar.append([comp_id, planned, 'planned'])
    return official_calendar
