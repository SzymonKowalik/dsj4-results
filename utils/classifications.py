
def ind_wc_classification(cursor):
    """Returns the individual World Cup classification.
    Returns: List of tuples containing the rank, name, country, and points of each competitor."""
    query = '''with max_pts as (
                    select max(pt) from (select sum(points) as pt from ind_results group by name) t
                )
                
                select rank() over(order by sum(points) desc) as rnk, name, country, sum(points)  as pt,
                       sum(points) - (select * from max_pts) as pts_diff
                from ind_results group by name order by pt desc'''
    cursor.execute(query)
    return 'Individual World Cup', cursor.fetchall()


def team_wc_classification(cursor):
    """Returns the team World Cup classification.
    Returns: List of tuples containing the rank, country, and points of each team."""

    query = '''with both_types as (
                select country, sum(points) as pt
                from ind_results group by country
                UNION ALL
                select country, sum(points) as pt
                from team_results group by country
                ), classification as (
                select rank() over(order by sum(pt) desc) as rnk, country, sum(pt) as pt
                from both_types
                group by country)
                
                select rnk, country, country, pt, pt - (select max(pt) from classification) as pt_loss
                from classification'''
    cursor.execute(query)
    return 'Team World Cup', cursor.fetchall()


def tournament_classification(cursor, name, comp_type, competition_ids, qualification_ids):
    """Returns the classification of a tournament.
    Parameters:
        cursor (sqlite3.Cursor): Cursor object to execute SQL commands.
        name (str): Name of the tournament.
        comp_type (int): Type of competition (points - 0 / notes - 1).
        competition_ids (tuple): Tuple of competition IDs.
        qualification_ids: Tuple of qualification IDs."""
    # Check competition type for classification
    if int(comp_type) == 0:
        comp_type = 'points'
    else:
        comp_type = 'note'
    #  Retrieves classification from database
    query = '''with classification as (
                select
                    rank() over(order by sum({}) desc) as rnk, name, country, round(sum({}), 1) as pt
                from ind_results
                where (comp_id in {} and comp_type in ('ind', 'team'))
                    or (comp_id in {} and comp_type='qual')
                group by name order by pt desc
                )
                
                select *, round(pt - (select max(pt) from classification), 1) as pt_loss
                from classification'''\
        .format(comp_type, comp_type, competition_ids, qualification_ids)

    classification = cursor.execute(query)
    results = []
    # Rounds results based on competition type
    for competitor in classification:
        if comp_type == 'note':
            *row, note = competitor
            results.append((*row, f'{note:.1f}'))
        else:
            *row, points = competitor
            results.append([*row, f'{points:.0f}'])
    return name, results


def read_tournaments():
    """Reads the tournaments.txt file and returns a list of tournament information in format:
    list of lists containing the name, competition type, and competition IDs of each tournament."""
    try:
        with open('./data/tournaments.txt', encoding='UTF-8') as file:
            return [prepare_tournament_info(line.rstrip().split(';')) for line in file
                    if not line.startswith('#') and line != '\n']
    except FileNotFoundError:
        open('./data/tournaments.txt', 'w')


def prepare_tournament_info(tournament):
    """
    Prepare tournament information for database by checking for correct format of tournament data
    and splitting the competition and qualification ids.

    Parameters:
        tournament: Tuple of tournament data in format (name, comp_type, competition_ids, qualification_ids)
                or  (name, comp_type, competition_ids)

    Returns:
        tuple : Tuple containing the name, comp_type, tuple of competition_ids and tuple of qualification_ids.
    """
    if len(tournament) == 3:
        name, comp_type, competition_ids = tournament
        qualification_ids = (0, 0)
    else:
        name, comp_type, competition_ids, qualification_ids = tournament
        # Convert qualification_ids to valid format
        try:
            qualification_ids = tuple(int(qual_id) for qual_id in qualification_ids.split(','))
            # Fix error with sql adding
            if len(qualification_ids) == 1:
                qualification_ids = (0, qualification_ids[0])
        except ValueError:
            raise ValueError('Wrong qualification ids format in tournaments.txt')
    # Check if comp_type is in valid format
    if int(comp_type) not in (0, 1):
        raise ValueError('Wrong competition type in tournaments.txt')
    # Check if competition_ids are in valid format
    try:
        competition_ids = tuple(int(comp_id) for comp_id in competition_ids.split(','))
    except ValueError:
        raise ValueError('Wrong competition ids format in tournaments.txt')

    return name, comp_type, competition_ids, qualification_ids


def create_all_tournaments_classifications(cursor, tournaments):
    """Generates the classifications for individual World Cup, team World Cup,
    and the tournaments listed in the tournaments.txt file.
    Parameters: cursor (sqlite3.Cursor): Cursor object to execute SQL commands.
    Returns: List of lists containing the classification for each competition."""
    tournament_classifications = [
        ind_wc_classification(cursor),
        team_wc_classification(cursor)
    ]

    for tournament in tournaments:
        name, comp_type, competition_ids, qualification_ids = tournament
        tournament_result = tournament_classification(cursor, name, comp_type, competition_ids, qualification_ids)
        tournament_classifications.append(tournament_result)
    # Get all tournament names
    tournaments = [['Individual World Cup'], ['Team World Cup'], *tournaments]
    return tournament_classifications, tournaments
