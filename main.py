from utils.create_database import initialise_tables, process_competition_files
from utils.classifications import create_tournament_classifications, read_tournaments
from utils.calendar import return_calendar, calendar_with_tournaments
import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template(
        'index.html',
        calendar=calendar_all,
        tournaments=tournaments,
        classifications=classifications)


if __name__ == '__main__':
    con = sqlite3.connect('./data/results.db')
    cur = con.cursor()
    initialise_tables(cur)
    process_competition_files(cur, con)
    classifications, tournaments = create_tournament_classifications(cur, read_tournaments())
    calendar_all = calendar_with_tournaments(cur)

    app.run(debug=True)