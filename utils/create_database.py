import os
import re
import sqlite3
from utils.point_systems import DEFAULT_POINTS_IND, DEFAULT_POINTS_TEAM


def clear_results_folder(stats_path):
    """ Removes unnecessary files from the project results folder.
    Parameters: stats_path (str): Path to the directory to clean."""
    for file in os.scandir(stats_path):
        if ' after ' in file.name:
            os.remove(file)


def prepare_file_individual(file_path, comp_type):
    """
       Prepare file for competition results data.

       Parameters:
           file_path (str): path to the file to be prepared
           comp_type (str): type of competition - 'ind' for individual or 'qual' for qualification.

       Returns:
           tuple:
               comp_type (str): type of competition
               hill_name (str): name of the hill where the competition took place
               results (list): a list of lists containing the processed competition results
       """
    with open(file_path, 'r', encoding='UTF-8') as file:
        file_content = [line.strip() for line in file]

    # Fix splitting when jumper name has maximum length
    # Add a space before country name
    for i, row_content in enumerate(file_content):
        file_content[i] = re.sub(r"\b[A-Z]{3}\b", r" \g<0>", row_content)

    # Get individual results into lists
    results = [re.split(r'\s{2,}', line) for line in file_content[4:]]

    if comp_type == 'ind':
        # Gets hill name from second line
        hill_name = file_content[1].replace(' Competition Final Results', '')

        # Fill rows with equal position
        for i, row in enumerate(results):
            if '.' not in row[0]:
                row.insert(0, results[i - 1][0])

        # Fill 2nd jump column with ''
        for i, row in enumerate(results):
            if len(row) < 7:
                row.insert(5, '')

        # Make place integer and last 3 columns float values
        for row in results:
            row[0] = int(row[0][:-1])
            row[4] = float(row[4].removesuffix('*')[:-2])
            if row[5] != '':
                row[5] = float(row[5].removesuffix('*')[:-2])
            row[6] = float(row[6])

    elif comp_type == 'qual':
        # Gets hill name from second line
        hill_name = file_content[1].replace(' Qualification Results', '')

        # Fill rows with equal position
        for i, row in enumerate(results):
            if '.' not in row[0]:
                row.insert(0, results[i - 1][0])

        # Make place integer and 2 last columns float values
        for i, row in enumerate(results):
            row[0] = int(row[0][:-1])
            row[4] = float(row[4].removesuffix('*')[:-2])
            row[5] = float(row[5])
            if len(row) == 7:
                results[i] = row[:-1]
            results[i].insert(5, '')
    else:
        raise ValueError("Invalid comp_type. Must be 'ind' or 'qual'.")

    return comp_type, hill_name, results


def prepare_file_team(file_path):
    """
        Prepare file for team competition results data.

        Parameters:
            file_path (str): path to the file to be prepared

        Returns:
            tuple:
                hill_name (str): name of the hill where the competition took place
                team_comp_results (list): a list of lists containing the processed team competition results
                ind_comp_results (list): a list of lists containing the processed individual competition results
        """
    with open(file_path, 'r', encoding='UTF-8') as file:
        file_content = [line.strip() for line in file if line != '\n']

        # Gets hill name from second line
        hill_name = file_content[1].replace(' Competition Final Results', '')

        # Get individual results into lists
        results = [re.split(r'\s{2,}', line) for line in file_content[3:]]

        # Fill rows with equal position
        for i, row in enumerate(results):
            if '.' not in row[0]:
                row.insert(0, results[i - 1][0])

        # Fill rows with country position
        for i, row in enumerate(results):
            if len(row) != 5:
                row.insert(3, results[i - 1][3])

        # Save team and individual results separately
        team_comp_results = []
        ind_comp_results = []
        # for country results
        for team_row in range(0, len(results), 5):
            team_results = results[team_row]
            team_results[0] = int(team_results[0][:-1])
            team_results[4] = float(team_results[4])
            team_comp_results.append(team_results[:5])
        # for individual results
        for ind_row in range(0, len(results), 1):
            if ind_row % 5 == 0:
                continue
            ind_results = results[ind_row]
            # Fill 2nd jump column with ''
            for i, row in enumerate(results):
                if len(row) < 8:
                    row.insert(5, '')
            ind_results[0] = int(ind_results[0][:-1])
            ind_results[1] = int(ind_results[1].replace('-', ''))
            ind_results[4] = float(ind_results[4].removesuffix('*')[:-2])
            if ind_results[5] != '':
                ind_results[5] = float(ind_results[5].removesuffix('*')[:-2])
            ind_results[6] = float(ind_results[6])
            ind_comp_results.append(ind_results[:-1])

    return hill_name, team_comp_results, ind_comp_results


def get_results_path(stats_path):
    """
    Returns a sorted list of file names in the DSJ4 stats directory.
    Parameters:
        stats_path (str): Path to the DSJ4 stats directory.
    Returns:
        list: List of file names (str).
    """
    files = [file.name for file in os.scandir(stats_path)]
    files.sort(key=lambda s: os.path.getmtime(os.path.join(stats_path, s)))
    return [f'{stats_path}/{file}' for file in files]


def get_competition_type(file_name):
    """Converts competition type from file name
    into format used in code."""
    if 'Team' in file_name:
        return 'team'
    elif 'Competition' in file_name:
        return 'ind'
    elif 'Qualification' in file_name:
        return 'qual'
    else:
        raise ValueError('Wrong file in DSJ4 stats folder')


def process_competition_files(cursor, db_con):
    """
    Processes ski jump competition files and stores the data into a database.
    This function uses the current logged in user's Documents/Deluxe Ski Jump 4/Stats folder as the default location to look for ski jump files.
    It then uses the passed cursor and db_con to add the data to the database.

    Parameters:
        cursor: cursor object to execute SQL commands.
        db_con: connection object to the database.
    """
    current_user = os.getlogin()
    stats_path = rf'C:\Users\{current_user}\Documents\Deluxe Ski Jump 4\Stats'
    file_names = get_results_path(stats_path)

    comp_id = 1
    for file_name in file_names:
        comp_type = get_competition_type(file_name)
        file_path = f"{stats_path}\{file_name}"
        try:
            if comp_type == 'team':
                file_data = prepare_file_team(file_name)
                add_team_competition_results(cursor, db_con, comp_id, file_data)
                print(f'Added team {comp_type} with id={comp_id}')
            else:
                file_data = prepare_file_individual(file_name, comp_type)
                add_individual_competition_results(cursor, db_con, comp_id, file_data)
                print(f'Added ind {comp_type} with id={comp_id}')
        except sqlite3.IntegrityError as e:
            print(e)
        if comp_type != 'qual':
            comp_id += 1


def add_individual_competition_results(cursor, db_con, comp_id, file_data):
    """Adds team competition results to the database if not added yet.
        Parameters:
            cursor (sqlite3.Cursor): Cursor object to execute SQL commands.
            db_con (sqlite3.Connection): Connection object to the database.
            comp_id (int): ID of the competition.
            file_data (tuple): Tuple containing hill name (str) and results (list of lists).
    """
    # Extract file_data
    comp_type, hill_name, results = file_data
    # Check if competition has already been added
    cursor.execute(f"SELECT count(*) FROM competitions where comp_id='{comp_id}' and comp_type='{comp_type}'")
    if cursor.fetchone()[0] != 0:
        raise sqlite3.IntegrityError(
            f'Competition with comp_id={comp_id} and comp_type={comp_type} has already been added.')

    insert_competitions = f"INSERT INTO competitions (comp_id, comp_type, hill) VALUES ('{comp_id}', '{comp_type}', '{hill_name}')"
    insert_results = 'INSERT INTO ind_results (comp_id, comp_type, place, number, name, country, jump1, jump2, note, points) VALUES '
    for row in results:
        if comp_type == 'ind':
            points = DEFAULT_POINTS_IND.get(row[0], 0)
        else:
            points = 0
        insert_results += "('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}), ".format(comp_id, comp_type, *row, points)
    cursor.execute(insert_competitions)
    db_con.commit()
    cursor.execute(insert_results[:-2])
    db_con.commit()


def add_team_competition_results(cursor, db_con, comp_id, file_data):
    """Adds competition results to the database if not added yet.
        Parameters:
            cursor (sqlite3.Cursor): Cursor object to execute SQL commands.
            db_con (sqlite3.Connection): Connection object to the database.
            comp_id (int): ID of the competition.
            file_data (tuple): Tuple containing hill name (str) and results (list of lists).
    """
    # Extract file_data
    hill_name, team_comp_results, ind_comp_results = file_data
    # Check if competition has already been added
    cursor.execute(f"SELECT count(*) FROM competitions where comp_id='{comp_id}'")
    if cursor.fetchone()[0] != 0:
        raise sqlite3.IntegrityError(f"Competition with comp_id={comp_id} and comp_type=team has already been added.")

    insert_competitions = f"INSERT INTO competitions (comp_id, comp_type, hill) VALUES ('{comp_id}', 'team', '{hill_name}')"
    insert_ind_results = 'INSERT INTO ind_results (comp_id, comp_type, place, number, name, country, jump1, jump2, note, points) VALUES '
    for row in ind_comp_results:
        points = 0
        insert_ind_results += "('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}), ".format(comp_id, 'team', *row, points)
    insert_team_results = f"INSERT INTO team_results (comp_id, place, number, team_name, country, note, points) VALUES"
    for row in team_comp_results:
        points = DEFAULT_POINTS_TEAM.get(row[0], 0)
        insert_team_results += "('{}', '{}', '{}', '{}', '{}', '{}', '{}'), ".format(comp_id, *row, points)
    cursor.execute(insert_competitions)
    db_con.commit()
    cursor.execute(insert_ind_results[:-2])
    db_con.commit()
    cursor.execute(insert_team_results[:-2])
    db_con.commit()


def initialise_tables(cursor):
    """Initializes the results and competitions tables in the database."""
    cursor.execute('CREATE TABLE IF NOT EXISTS ind_results (id INTEGER PRIMARY KEY AUTOINCREMENT, comp_id INTEGER, '
                   'comp_type varchar(4), place INTEGER, number INTEGER, name varchar(50), country VARCHAR(3), '
                   'jump1 float(3,1), jump2 float(3,1), note float(3,1), points INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS team_results (id INTEGER PRIMARY KEY AUTOINCREMENT, comp_id INTEGER, '
                   'place INTEGER, number INTEGER, team_name varchar(50), country varchar(3),'
                   'note float(4,1), points INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS competitions (id INTEGER PRIMARY KEY AUTOINCREMENT, comp_id INTEGER, '
                   'comp_type varchar(4), hill varchar(50))')
