from utils.create_database import initialise_tables, fill_database_with_results
from utils.classifications import create_tournament_classifications
from utils.excel_options import save_results_in_excel
from utils.calendar import return_calendar
import sqlite3


def main():
    """This function is the entry point for the program. It initializes the necessary database tables,
    fills them with results data from the DSJ4 stats directory, generates tournament classifications,
    creates a calendar of all competitions, and saves the classifications and calendar to an Excel file."""
    con = sqlite3.connect('./data/results.db')
    cur = con.cursor()
    initialise_tables(cur)
    fill_database_with_results(cur, con)

    classifications, tournaments = create_tournament_classifications(cur)
    calendar = return_calendar(cur)
    save_results_in_excel(classifications, calendar, tournaments)


if __name__ == '__main__':
    main()
