from utils.create_database import initialise_tables, process_competition_files
from utils.classifications import create_all_tournaments_classifications, read_tournaments
from utils.calendar import calendar_with_tournaments, get_tournament_calendar, return_calendar
from utils.results import individual_competition_results, individual_results, team_results, team_competition_results
import sqlite3
from flask import Flask, render_template, request
import re

app = Flask(__name__)


@app.route('/')
def index():
    classifications, tournaments, calendar_all = refresh(cur, con)
    return render_template(
        'index.html',
        calendar=calendar_all,
        tournaments=tournaments,
        classifications=classifications)


@app.route('/competition/<comp_id>')
def competition(comp_id):
    classifications, tournaments, calendar_all = refresh(cur, con)
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
    classifications, tournaments, calendar_all = refresh(cur, con)
    # Regex for team as name
    country = re.search(r"^[A-Z]{3}$", name)
    if country:
        results = team_results(cur, name)
        template = 'competitor_team.html'
        country = name
    else:
        results, country = individual_results(cur, name)
        template = 'competitor_ind.html'
    return render_template(template,
                           tournaments=tournaments,
                           name=name,
                           results=results,
                           country=country)


@app.route('/tournament/<tournament_name>')
def tournament(tournament_name):
    classifications, tournaments, calendar_all = refresh(cur, con)
    for tournament in classifications:
        if tournament_name == tournament[0]:
            tournament_data = tournament[1]
    tournament_calendar = get_tournament_calendar(calendar, tournaments, tournament_name)
    return render_template('tournament.html',
                           tournaments=tournaments,
                           tournament_name=tournament_name,
                           tournament_data=tournament_data,
                           tournament_calendar=tournament_calendar)


def refresh(cur, con):
    process_competition_files(cur, con)
    classifications, tournaments = create_all_tournaments_classifications(cur, read_tournaments())
    calendar_all = calendar_with_tournaments(cur)
    return classifications, tournaments, calendar_all


if __name__ == '__main__':
    con = sqlite3.connect('./data/results.db', check_same_thread=False)
    cur = con.cursor()
    initialise_tables(cur)
    classifications, tournaments, calendar_all = refresh(cur, con)
    calendar = return_calendar(cur)

    app.run(debug=True)
