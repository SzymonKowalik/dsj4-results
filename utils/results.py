
def individual_competition_results(cursor, comp_id):
    """Retrieve the results of an individual competition by competition id."""
    query = """select place, name, country, jump1, jump2, note from ind_results
                where comp_id={} and comp_type = 'ind'""".format(comp_id)
    cursor.execute(query)
    header_row = ['place', 'name', 'country', 'jump1', 'jump2', 'note']
    return [header_row, *cursor.fetchall()]


def qualifying_results(cursor, comp_id):
    """Retrieve the results of a qualifying by competition id."""
    query = """select place, name, country, jump1, note from ind_results
                    where comp_id={} and comp_type = 'qual'""".format(comp_id)
    cursor.execute(query)
    header_row = ['place', 'name', 'country', 'jump', 'note']
    return [header_row, *cursor.fetchall()]


def team_competition_results(cursor, comp_id):
    """Retrieve the results of a team competition by competition id."""
    query = """select place, country, country, note
                from team_results where comp_id={}""".format(comp_id)
    cursor.execute(query)
    header_row = ['place', 'name', 'country', 'note']
    return [header_row, *cursor.fetchall()]


def team_ind_competition_results(cursor, comp_id):
    """Retrieve the individual results of a team competition by competition id."""
    query = """select rank() over(order by note desc) as ind_rank, name, 
                country, jump1, jump2, note, place from ind_results
                where comp_id={} order by ind_rank""".format(comp_id)
    cursor.execute(query)
    header_row = ['ind_rank', 'name', 'country', 'jump1', 'jump2', 'note', 'place']
    return [header_row, *cursor.fetchall()]


def individual_results(cursor, name):
    """Retrieve the results of an individual athlete by their name.
    The results are not retrieved for qualification rounds."""
    query = """select comp_id, comp_type, hill, place, jump1, jump2, note
                from ind_results join competitions using(comp_id, comp_type)
                where name='{}' and comp_type != 'qual'""".format(name)
    cursor.execute(query)
    header_row = ['comp_id', 'comp_type', 'hill', 'place', 'jump1', 'jump2', 'note']
    results = cursor.fetchall()

    query_country = """select distinct country from ind_results where name='{}'""".format(name)
    cursor.execute(query_country)
    country = str(*cursor.fetchall()[0])
    return [header_row, *results], country


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
