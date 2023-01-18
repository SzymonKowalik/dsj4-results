def individual_stats(cursor, name):
    """Get individual statistics for given competitor from database"""
    query = """SELECT ROUND(AVG(place), 1), COUNT(*), COUNT(IIF(place<=30,1,NULL)), 
    COUNT(IIF(place<=10,1,NULL)), COUNT(IIF(place<=3,1,NULL)), COUNT(IIF(place=1,1,NULL))
                FROM ind_results WHERE name='{}' and comp_type='ind'""".format(name)
    cursor.execute(query)
    stats = cursor.fetchall()
    header = ['AVG Place', 'Competitions', 'TOP 30', 'TOP 10', 'TOP 3', 'TOP 1']
    return [header, *stats]


def team_ind_stats(cursor, country):
    """Get all individual statistics for given country from database"""
    query = """with jumper_number as (
                    SELECT count(DISTINCT name) from ind_results where country='{}'
                )
                
                SELECT (select * from jumper_number), ROUND(AVG(place), 1), COUNT(*), COUNT(IIF(place<=30,1,NULL)),
                COUNT(IIF(place<=10,1,NULL)), COUNT(IIF(place<=3,1,NULL)), COUNT(IIF(place=1,1,NULL))
                FROM ind_results
                WHERE country='{}' and comp_type='ind'""".format(country, country)
    cursor.execute(query)
    stats = cursor.fetchall()
    header = ['Jumpers', 'AVG Place', 'Competitions', 'TOP 30', 'TOP 10', 'TOP 3', 'TOP 1']
    return [header, *stats]


def team_team_stats(cursor, country):
    """Get all team statistics for given country from database"""
    query = """SELECT ROUND(AVG(place), 1), COUNT(*), COUNT(IIF(place<=8,1,NULL)),
                    COUNT(IIF(place<=3,1,NULL)), COUNT(IIF(place=1,1,NULL))
                FROM team_results
                WHERE country='{}'""".format(country)
    cursor.execute(query)
    stats = cursor.fetchall()
    # If team did not enter any competitions
    if stats[0][0] is None:
        return None
    else:
        header = ['AVG Place', 'Competitions', 'TOP 8', 'TOP 3', 'TOP 1']
        return [header, *stats]


def team_competitors(cursor, country):
    """Get all competitors from given country and their world cup points and place from database"""
    query = """with world_cup as (
                    select rank() over(order by sum(points) desc) as rnk, name, country, sum(points) as pt
                    from ind_results group by name order by pt desc
                )
                
                select name, pt, rnk from world_cup where country='{}'""".format(country)
    cursor.execute(query)
    stats = cursor.fetchall()
    header = ['Name', 'World Cup Points', 'World Cup Place']
    return [header, *stats]


def individual_all_tournaments(cursor, tournaments, name):
    """Returns all individual tournament results for given competitor."""
    results = []
    # World cup
    query = """with world_cup as (
                    select rank() over(order by sum(points) desc) as rnk, name, country, sum(points) as pt
                    from ind_results group by name order by pt desc
                )

                select pt, rnk from world_cup where name='{}'""".format(name)
    cursor.execute(query)
    results.append(['Individual World Cup', *cursor.fetchall()])
    # Rest of tournaments
    for tournament in tournaments[2:]:
        tournament_name, type, comp_ids, qual_ids = tournament
        if type == '0':
            type = 'points'
        else:
            type = 'note'
        query = """with tournament as (
                        select rank() over(order by sum({}) desc) as rnk, name, round(sum({}), 1) as pt
                        from ind_results where comp_id in {} and comp_type in ('ind', 'team') or
                        comp_id in {} and comp_type = 'qual' group by name order by pt desc
                    )

                    select pt, rnk from tournament where name='{}'""".format(type, type, comp_ids, qual_ids, name)
        cursor.execute(query)
        classification = cursor.fetchall()
        # If classification has competitions added or not
        if classification:
            if type == 'points':
                # Convert points to Integer to avoid .0 in table, data from database in list(tuple(...))
                points, place = classification[0]
                results.append([tournament_name, [int(points), place]])
            else:
                results.append([tournament_name, *classification])
        else:
            results.append([tournament_name, ('-', '-')])
    return [['Tournament Name', ('Points/Note', 'Place')], *results]
