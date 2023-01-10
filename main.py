from utils.create_database import initialise_tables, process_competition_files
from utils.classifications import create_tournament_classifications, read_tournaments
from utils.calendar import return_calendar, calendar_with_tournaments
from utils.results import individual_competition_results, individual_results, team_results, team_competition_results
import sqlite3
from flask import Flask, render_template, request
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template(
        'index.html',
        calendar=calendar_all,
        tournaments=tournaments,
        classifications=classifications)


@app.route('/competition/<comp_id>')
def competition(comp_id):
    hill_name = request.args.get('hill_name')
    comp_type = request.args.get('comp_type')
    print(hill_name, comp_type)
    if comp_type == 'ind':
        results = individual_competition_results(cur, comp_id)
    else:
        results = team_competition_results(cur, comp_id)
    return render_template('competition.html',
                           results=results,
                           hill_name=hill_name)



@app.route('/competitor/<name>')
def competitor(name):
    # Regex for team as name
    country = re.search(r"^[A-Z]{3}$", name)
    if country:
        results = team_results(cur, name)
        template = 'competitor_team.html'
    else:
        results = individual_results(cur, name)
        template = 'competitor_ind.html'
    return render_template(template,
                           name=name,
                           results=results)


if __name__ == '__main__':
    con = sqlite3.connect('./data/results.db', check_same_thread=False)
    cur = con.cursor()
    initialise_tables(cur)
    process_competition_files(cur, con)
    classifications, tournaments = create_tournament_classifications(cur, read_tournaments())
    calendar_all = calendar_with_tournaments(cur)

    app.run(debug=True)