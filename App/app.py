
from flask import Flask

from flask import make_response,redirect,request, url_for,abort,Response, render_template,flash,session
from werkzeug.urls import url_parse
import altair as alt
import pandas as pd
from vega_datasets import data
from flask import jsonify
from App.forms import selectYear


ENV = "local"

# My own MongoDB Cluster
# app.config['MONGO_DBNAME'] = 'SportsBet'
# app.config['MONGO_URI'] = 'mongodb+srv://admin:ads2sportsbet@ads-2.l7gr9.mongodb.net/SportsBet?retryWrites=true&w=majority'

app = Flask(__name__)


app.config['SECRET_KEY'] = 'dcqJQC6nDLEyz3k5'
app.config['SESSION_PROTECTION'] = 'strong'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)
# migrate = Migrate(app, db)


#from App.models import


@app.errorhandler(404)
def error_not_found(error):
    return render_template('error/not_found.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error/505.html'), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route("/data/best_team/<year>/<top>")
def homeAdv(year,top):
    year = int(year)
    if top =="top":
        return bestTeamPlot(year,True)
    return bestTeamPlot(year,False)


def bestTeamPlot(year,top):

    bigDf = pd.read_csv("App/Data/CumulativeSeasons.csv")

    dfSeason = bigDf[bigDf['season'] == str(year+2000)+"/"+str((year+1)+2000)]

    if top:
        df = dfSeason.groupby(['result', 'team_long_name']).size()['won'].sort_values(ascending=False)[:5]
    else:
        df = dfSeason.groupby(['result', 'team_long_name']).size()['won'].sort_values()[:5]
    teamList = df.index.tolist()

    num_players = 11
    df_won = []
    df_lost = []
    df_draw = []
    for i in df.index:
        won = (dfSeason.groupby(['team_long_name', "result"]).size()[i][2]) / num_players
        lost = (dfSeason.groupby(['team_long_name', "result"]).size()[i][1]) / num_players
        draw = (dfSeason.groupby(['team_long_name', "result"]).size()[i][0]) / num_players

        df_won.append(won)
        df_lost.append(lost)
        df_draw.append(draw)
    best = pd.DataFrame({'Team': teamList, 'Wins': df_won, 'Losts': df_lost, 'Draw': df_draw})

    chart = alt.Chart(pd.melt(best, id_vars=['Team'], var_name='Result', value_name='Total'),height=600,width=159).mark_bar().encode(
        alt.X('Result:N', axis=alt.Axis(title="")),
        alt.Y('Total:Q', axis=alt.Axis(title='Total', grid=False)),
        alt.Tooltip(["Total:Q"]),
        color=alt.Color('Result:N'),
        column=alt.Column('Team:O',sort=alt.EncodingSortField("Total", op='max',order='descending'))
    ).configure_view(
        stroke='transparent'
    ).interactive()

    return chart.to_json()


@app.route("/data/goalsGame")
def goalsGame():

    goals =pd.read_csv('App/Data/GoalsLeague.csv')

    topleague = ['Ligue 1', '1. Bundesliga', 'Premier League', 'Eredivisie', 'LIGA BBVA', 'Serie A']

    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['season'], empty='none')

    line = alt.Chart(goals).mark_line().encode(
        x=alt.X('season', title='Season'),
        y=alt.Y('match_goals:Q', scale=alt.Scale(domain=[2.2, 3.4]), title='Goals per game'),
        color=alt.Color('league:N', scale=alt.Scale(domain=topleague))
    )
    selectors = alt.Chart(goals).mark_point().encode(
        x='season',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )
    goal_last = goals[goals['season'] == '2015/2016']

    labels = alt.Chart(goal_last).mark_text(align='left', dx=3).encode(
        alt.X('season'),
        alt.Y('match_goals:Q', scale=alt.Scale(domain=[2.2, 3.4])),
        alt.Text('league'),
        alt.Color('league:N', legend=None, scale=alt.Scale(domain=topleague))
    )
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )
    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'match_goals:Q', alt.value(' '), format='.2f')
    )
    rules = alt.Chart(goals).mark_rule(color='gray').encode(x='season',).transform_filter(nearest)

    chart = alt.layer(line, selectors, labels, points, rules, text).properties(width=1000, height=500).interactive()

    return chart.to_json()


# render cars.html page
@app.route("/dashboard")
def statistics():
    form = selectYear(request.form)

    return render_template("dashboard.html",form=form)


if __name__ == '__main__':
    app.run()
