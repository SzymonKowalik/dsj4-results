from utils.create_database import initialise_tables, process_competition_files
from utils.classifications import create_all_tournaments_classifications, read_tournaments
from utils.calendar import calendar_with_tournaments, get_tournament_calendar
from utils.results import individual_competition_results, individual_results, team_results, team_competition_results,\
    team_ind_competition_results, qualifying_results
from utils.statistics import individual_stats, team_ind_stats, team_competitors, individual_all_tournaments,\
    team_team_stats, competitors_stats
import sqlite3
from flask import Flask, render_template, request
import re

# Initialise flask app and db connection
app = Flask(__name__)
con = sqlite3.connect('./data/results.db', check_same_thread=False)
cur = con.cursor()
initialise_tables(cur)


@app.route('/')
def index():
    classifications, tournaments, calendar_all = refresh()
    stats = competitors_stats(cur)
    return render_template(
        'index.html',
        calendar=calendar_all,
        tournaments=tournaments,
        classifications=classifications,
        stats=stats)


@app.route('/competition/<comp_id>')
def competition(comp_id):
    classifications, tournaments, calendar_all = refresh()
    hill_name = request.args.get('hill_name')
    comp_type = request.args.get('comp_type')
    if comp_type in ('ind', 'ind*'):
        ind_results = individual_competition_results(cur, comp_id)
        qual_results = qualifying_results(cur, comp_id)
        return render_template('competition_ind.html',
                               tournaments=tournaments,
                               ind_results=ind_results,
                               qual_results=qual_results,
                               hill_name=hill_name)
    else:
        team_results = team_competition_results(cur, comp_id)
        ind_results = team_ind_competition_results(cur, comp_id)
        return render_template('competition_team.html',
                               tournaments=tournaments,
                               team_results=team_results,
                               ind_results=ind_results,
                               hill_name=hill_name)


@app.route('/competitor/<name>')
def competitor(name):
    classifications, tournaments, calendar_all = refresh()
    # Regex for team as name
    country = re.search(r"^[A-Z]{3}$", name)
    if country:
        results = team_results(cur, name)
        template = 'competitor_team.html'
        ind_stats = team_ind_stats(cur, name)
        team_stats = team_team_stats(cur, name)
        competitors = team_competitors(cur, name)
        return render_template(template,
                               tournaments=tournaments,
                               name=name,
                               results=results,
                               country=name,
                               ind_stats=ind_stats,
                               team_stats=team_stats,
                               competitors=competitors)
    else:
        results, country = individual_results(cur, name)
        template = 'competitor_ind.html'
        ind_stats = individual_stats(cur, name)
        tournament_results = individual_all_tournaments(cur, tournaments, name)
        return render_template(template,
                               tournaments=tournaments,
                               name=name,
                               results=results,
                               country=country,
                               stats=ind_stats,
                               tournament_results=tournament_results)


@app.route('/tournament/<tournament_name>')
def tournament(tournament_name):
    classifications, tournaments, calendar_all = refresh()
    for tournament in classifications:
        if tournament_name == tournament[0]:
            tournament_data = tournament[1]
    tournament_calendar = get_tournament_calendar(calendar_all, tournaments, tournament_name)
    return render_template('tournament.html',
                           tournaments=tournaments,
                           tournament_name=tournament_name,
                           tournament_data=tournament_data,
                           tournament_calendar=tournament_calendar)


def refresh():
    process_competition_files(cur, con)
    classifications, tournaments = create_all_tournaments_classifications(cur, read_tournaments())
    calendar_all = calendar_with_tournaments(cur)
    return classifications, tournaments, calendar_all


if __name__ == '__main__':
    app.run(debug=True)
    # TODO Calculate average place with qualification
    # TODO Add custom tournaments to main calendar
    # TODO Indicate qualification in calendar
