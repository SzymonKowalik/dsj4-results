from utils.create_database import initialise_tables, process_competition_files
from utils.classifications import create_all_tournaments_classifications, read_tournaments
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
    if comp_type == 'ind':
        results = individual_competition_results(cur, comp_id)
    else:
        results = team_competition_results(cur, comp_id)
    return render_template('competition.html',
                           tournaments=tournaments,
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
                           tournaments=tournaments,
                           name=name,
                           results=results)


@app.route('/tournament/<tournament_name>')
def tournament(tournament_name):
    for tournament in classifications:
        print(tournament[0])
        print(tournament_name)
        if tournament_name == tournament[0]:
            tournament_data = tournament[1]
    return render_template('tournament.html',
                           tournaments=tournaments,
                           tournament_name=tournament_name,
                           tournament_data=tournament_data)


if __name__ == '__main__':
    con = sqlite3.connect('./data/results.db', check_same_thread=False)
    cur = con.cursor()
    initialise_tables(cur)
    process_competition_files(cur, con)
    classifications, tournaments = create_all_tournaments_classifications(cur, read_tournaments())
    calendar_all = calendar_with_tournaments(cur)

    app.run(debug=True)