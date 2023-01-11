
def individual_competition_results(cursor, comp_id):
    """Retrieve the results of an individual competition by competition id.
    This returns the place, name, country, jump1, jump2 and note of the individual competitors. """
    query = """select place, name, country, jump1, jump2, note from ind_results
                where comp_id={} and comp_type != 'qual'""".format(comp_id)
    cursor.execute(query)
    header_row = ['place', 'name', 'country', 'jump1', 'jump2', 'note']
    return [header_row, *cursor.fetchall()]


def team_competition_results(cursor, comp_id):
    """Retrieve the results of a team competition by competition id.
    This returns the place, team_name and note of the teams."""
    query = """select place, team_name, note
                from team_results where comp_id={}""".format(comp_id)
    cursor.execute(query)
    header_row = ['place', 'name', 'note']
    return [header_row, *cursor.fetchall()]


def individual_results(cursor, name):
    """Retrieve the results of an individual athlete by their name.
    This returns the comp_id, comp_type, hill, place, jump1, jump2 and note of the individual athlete.
    The results are not retrieved for qualification rounds."""
    query = """select comp_id, comp_type, hill, place, jump1, jump2, note
                from ind_results join competitions using(comp_id, comp_type)
                where name='{}' and comp_type != 'qual'""".format(name)
    cursor.execute(query)
    header_row = ['comp_id', 'comp_type', 'hill', 'place', 'jump1', 'jump2', 'note']
    return [header_row, *cursor.fetchall()]


def team_results(cursor, country):
    """Retrieve the results of a team and individual competitions by a country name.
    This returns the results of both team and individual competitions of the country."""
    # Team competition results
    query = """select comp_id, hill, place, note
                from team_results join competitions using(comp_id)
                where country='{}'""".format(country)
    cursor.execute(query)
    header_row = ['comp_id', 'hill', 'place', 'note']
    results_team = [header_row, *cursor.fetchall()]
    # Individual competition results
    query = """select comp_id, hill, name, place, jump1, jump2, note
                from ind_results join competitions using(comp_id, comp_type)
                where country='{}' and comp_type == 'ind'""".format(country)
    cursor.execute(query)
    header_row = ['comp_id', 'hill', 'name', 'place', 'jump1', 'jump2', 'note']
    results_ind = [header_row, *cursor.fetchall()]
    # Return both lists
    return results_team, results_ind
