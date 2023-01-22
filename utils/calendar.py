from itertools import zip_longest
from utils.classifications import read_tournaments


def read_planned_calendar():
    """Reads the planned_calendar.txt file and returns a list of planned competition names."""
    try:
        with open('./data/planned_calendar.txt', encoding='UTF-8') as file:
            return [line.rstrip().split(';') for line in file if not line.startswith('#') and line != '\n']
    except FileNotFoundError:
        open('./data/planned_calendar.txt', 'w')


def return_calendar(cursor):
    """
    Returns an official calendar of ski jumping competitions by combining planned and completed competitions.
    Using the provided cursor, the function fetches the completed competitions from the database,
    and the planned calendar from the external source,
    Then it combine those and creating an official calendar of ski jumping competitions."""
    planned_calendar = read_planned_calendar()
    cursor.execute("SELECT hill, comp_type FROM competitions where comp_type != 'qual'")
    actual_calendar = [[hill[0], hill[1]] for hill in cursor.fetchall()]
    official_calendar = []
    for comp_id, calendar in enumerate(zip_longest(planned_calendar, actual_calendar), 1):
        planned, actual = calendar
        if actual is not None:
            official_calendar.append([comp_id, *actual, 'completed'])
        else:
            official_calendar.append([comp_id, *planned, 'planned'])
    return official_calendar


def calendar_with_tournaments(cursor):
    """
    Creates a calendar of ski jumping competitions and adds tournament information to it.
    Using the provided cursor, the function fetches the calendar of ski jumping competitions,
    then adds additional columns to it indicating the presence of a tournament and its type.

    Parameters:
        cursor : cursor object to execute SQL commands.

    Returns:
        list : A 2D list representing the calendar with tournament information added.
    """
    calendar = return_calendar(cursor)
    calendar.insert(0, ['id', 'hill', 'type', 'status'])
    tournament_data = read_tournaments()
    for tournament in tournament_data:
        name, comp_type, competition_ids, qualification_ids = tournament
        calendar[0].append(name)
        for comp_info in calendar[1:]:
            comp_id = comp_info[0]
            info = ''
            if comp_id in competition_ids:
                info += 'X'
            if comp_id in qualification_ids:
                info += '*'
            comp_info.append(info)
    return calendar


def get_tournament_calendar(calendar, tournaments, tournament_name):
    """Function searches for given tournament name in tournaments 2d list.
    Then it appends to new list all competitions which are included in tournament.
    Return tournament_calendar list ready for html table."""
    for tournament in tournaments[2:]:
        name, _, comp_ids, quali_ids = tournament
        if tournament_name == name:
            break
    else:
        return None
    tournament_calendar = []
    for comp_info in calendar:
        comp_id, comp_name, comp_type, comp_status, *_ = comp_info
        if comp_id in comp_ids:
            if comp_id in quali_ids:
                comp_type = f'{comp_type}*'
            tournament_calendar.append([comp_id, comp_name, comp_type, comp_status])
    return tournament_calendar
