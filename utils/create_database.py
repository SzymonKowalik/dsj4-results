import os
import re
import sqlite3
from utils.point_systems import DEFAULT_POINTS_IND


def clear_results_folder(stats_path):
    """ Removes unnecessary files from the project results folder.
    Parameters: stats_path (str): Path to the directory to clean."""
    for file in os.scandir(stats_path):
        if ' po ' in file.name:
            os.remove(file)


def prepare_file(file_path):
    """Prepares the file for further processing.
    Parameters: file_path (str): Path to the file to prepare.
    Returns: Tuple containing hill name (str) and results (list of lists)."""
    with open(file_path, 'r', encoding='UTF-8') as file:
        file_content = [line.strip() for line in file]

    # Fix splitting when jumper name has maximum length
    # Add a space before country name
    for i, row_content in enumerate(file_content):
        file_content[i] = re.sub(r"\b[A-Z]{3}\b", r" \g<0>", row_content)

    # Get individual results into lists
    results = [re.split(r'\s{2,}', line) for line in file_content[4:]]

    # Gets hill name from second line
    hill_name = file_content[1].replace('Wyniki konkursu', '')

    # Fill rows with equal position
    for i, row in enumerate(results):
        if '.' not in row[0]:
            row.insert(0, results[i-1][0])

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

    return hill_name, results


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


def add_competition_results(cursor, db_con, comp_id, file_data):
    """Adds competition results to the database if not added yet.
        Parameters:
            cursor (sqlite3.Cursor): Cursor object to execute SQL commands.
            db_con (sqlite3.Connection): Connection object to the database.
            comp_id (int): ID of the competition.
            file_data (tuple): Tuple containing hill name (str) and results (list of lists).
    """
    # Check if competition has already been added
    cursor.execute(f'SELECT count(*) FROM competitions where comp_id={comp_id}')
    if cursor.fetchone()[0] != 0:
        raise sqlite3.IntegrityError(f'Competition with id={comp_id} has already been added.')

    hill, results = file_data
    insert_competitions = f"INSERT INTO competitions VALUES ('{comp_id}', '{hill}')"
    insert_results = 'INSERT INTO results (comp_id, place, number, name, country, jump1, jump2, note, points) VALUES '
    for row in results:
        points = DEFAULT_POINTS_IND.get(row[0], 0)
        insert_results += "('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}), ".format(comp_id, *row, points)
    cursor.execute(insert_competitions)
    db_con.commit()
    cursor.execute(insert_results[:-2])
    db_con.commit()


def fill_database_with_results(cursor, db_con):
    """Fills the database with new results from DSJ4 stats.
    Parameters:
            cursor (sqlite3.Cursor): Cursor object to execute SQL commands.
            db_con (sqlite3.Connection): Connection object to the database.
    """
    current_user = os.getlogin()
    stats_path = rf'C:\Users\{current_user}\Documents\Deluxe Ski Jump 4\Stats'
    file_names = get_results_path(stats_path)

    for comp_id, file_name in enumerate(file_names, 1):
        file_data = prepare_file(file_name)
        try:
            add_competition_results(cursor, db_con, comp_id, file_data)
            print(f'Added competition with id={comp_id}')
        except sqlite3.IntegrityError as e:
            print(e)


def initialise_tables(cursor):
    """Initializes the results and competitions tables in the database."""
    cursor.execute('CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY AUTOINCREMENT, comp_id INTEGER, '
                   'place INTEGER, number INTEGER, name varchar(50), country VARCHAR(3), jump1 float(3,1), '
                   'jump2 float(3,1), note float(3,1), points INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS competitions (comp_id INTEGER PRIMARY KEY AUTOINCREMENT, '
                   'hill varchar(50))')
