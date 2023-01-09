
def ind_wc_classification(cursor):
    """Returns the individual World Cup classification.
    Returns: List of tuples containing the rank, name, country, and points of each competitor."""
    query = '''with max_pts as (
                    select max(pt) from (select sum(points) as pt from results group by name) t
                )
                
                select rank() over(order by sum(points) desc) as rnk, name, country, sum(points)  as pt,
                       sum(points) - (select * from max_pts) as pts_diff
                from results group by name order by pt desc'''
    cursor.execute(query)
    return 'Individual World Cup classification', cursor.fetchall()


def team_wc_classification(cursor):
    """Returns the team World Cup classification.
    Returns: List of tuples containing the rank, country, and points of each team."""

    query = '''with max_pts as (
                    select max(pt) from (select sum(points) as pt from results group by country) t
                )
                
                select rank() over(order by sum(points) desc) as rnk, country, sum(points) as pt,
                       sum(points) - (select * from max_pts) as pts_diff
                from results group by country order by pt desc'''
    cursor.execute(query)
    return 'Team World Cup classification', cursor.fetchall()


def tournament_classification(cursor, name, comp_type, competition_ids):
    """Returns the classification of a tournament.
    Parameters:
        cursor (sqlite3.Cursor): Cursor object to execute SQL commands.
        name (str): Name of the tournament.
        comp_type (int): Type of competition (points - 0 / notes - 1).
        competition_ids (tuple): Tuple of competition IDs."""
    if int(comp_type) == 0:
        comp_type = 'points'
    else:
        comp_type = 'note'

    query = '''with max_pts as (
                    select max(pt) from (select sum({}) as pt from results where comp_id in {} group by name) t
                )

                select rank() over(order by sum({}) desc) as rnk, name, country, sum({}) as pt,
                       sum({}) - (select * from max_pts) as pts_diff
                from results where comp_id in {} group by name order by pt desc'''\
        .format(comp_type, competition_ids, comp_type, comp_type, comp_type, competition_ids)

    classification = cursor.execute(query)
    results = []
    for competitor in classification:
        if comp_type == 'note':
            *row, points = competitor
            results.append((*row, f'{points:.1f}'))
        else:
            results.append([*competitor])
    return name, results


def read_tournaments():
    """Reads the tournaments.txt file and returns a list of tournament information in format:
    list of lists containing the name, competition type, and competition IDs of each tournament."""
    try:
        with open('./data/tournaments.txt', encoding='UTF-8') as file:
            return [line.rstrip().split(';') for line in file if not line.startswith('#') and line != '\n']
    except FileNotFoundError:
        open('./data/tournaments.txt', 'w')


def create_tournament_classifications(cursor):
    """Generates the classifications for individual World Cup, team World Cup,
    and the tournaments listed in the tournaments.txt file.
    Parameters: cursor (sqlite3.Cursor): Cursor object to execute SQL commands.
    Returns: List of lists containing the classification for each competition."""
    tournament_classifications = [
        ind_wc_classification(cursor),
        team_wc_classification(cursor)
    ]

    tournaments = read_tournaments()
    for tournament in tournaments:
        name, comp_type, competition_ids = tournament
        # Check if comp_type is in valid format
        if int(comp_type) not in (0, 1):
            raise ValueError('Wrong competition type in tournaments.txt')
        # Check if competition_ids are in valid format
        try:
            [int(comp_id) for comp_id in competition_ids.split(',')]
        except ValueError:
            raise ValueError('Wrong competition ids format in tournaments.txt')
        # Generate competition results
        competition_ids = f"({competition_ids})"
        tournament_result = tournament_classification(cursor, name, comp_type, competition_ids)
        tournament_classifications.append(tournament_result)
    return tournament_classifications, tournaments
