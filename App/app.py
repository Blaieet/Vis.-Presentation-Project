
from flask import Flask

from flask import make_response,redirect,request, url_for,abort,Response, render_template,flash,session
from werkzeug.urls import url_parse
import altair as alt
import pandas as pd
import numpy as np
from vega_datasets import data
from flask import jsonify
from App.forms import selectYear, chartSelect
import datetime


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


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/storytelling")
def storytelling():
    return render_template("storytelling.html")


@app.errorhandler(404)
def error_not_found(error):
    return render_template('error/not_found.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error/505.html'), 500

@app.route('/about')
def about():
    return render_template('about.html')


@app.route("/data/best_team/<year>/<top>")
def best(year,top):
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
        won = int((dfSeason.groupby(['team_long_name', "result"]).size()[i][2]) / num_players)
        lost = int((dfSeason.groupby(['team_long_name', "result"]).size()[i][1]) / num_players)
        draw = int((dfSeason.groupby(['team_long_name', "result"]).size()[i][0]) / num_players)

        df_won.append(won)
        df_lost.append(lost)
        df_draw.append(draw)
    best = pd.DataFrame({'Team': teamList, 'Wins': df_won, 'Losts': df_lost, 'Draw': df_draw})

    chart = alt.Chart(pd.melt(best, id_vars=['Team'], var_name='Result', value_name='Total'),height=400,width=165).mark_bar().encode(
        alt.X('Result:N', axis=alt.Axis(title="",labels=False)),
        alt.Y('Total:Q', axis=alt.Axis(title='Total', grid=False)),
        alt.Tooltip(["Total:Q"]),
        color=alt.Color('Result:N'),
        column=alt.Column('Team:O',sort=alt.EncodingSortField("Total", op='max',order='descending'),title="")
    ).configure_view(
        stroke='transparent'
    ).interactive()

    return chart.to_json()

@app.route("/data/messiCristiano")
def messiCristiano():
    finalDF = pd.read_csv("App/Data/messiCristiano.csv")
    finalDF['date'] = finalDF['date'].apply(lambda x: datetime.datetime(x, 1, 1))
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['date'], empty='none')

    line = alt.Chart(finalDF, height=360, width=980).mark_line().encode(
        x=alt.X('year(date):T', title='Year'),
        y=alt.Y('overall_rating:Q', scale=alt.Scale(domain=[85, 95]), title='Overall Rating'),
        color=alt.Color('player_name', title="Player"))

    selectors = alt.Chart(finalDF).mark_point().encode(
        x='year(date):T',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'overall_rating:Q', alt.value(' '), format='.2f')
    )

    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    rules = alt.Chart(finalDF).mark_rule(color='gray').encode(x='date').transform_filter(nearest)

    chart = (line + selectors + rules + text + points)

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

    chart = alt.layer(line, selectors, labels, points, rules, text).properties(width=1199, height=300).interactive()

    return chart.to_json()

@app.route("/data/homeAdv")
def homeAdv():

    adv = pd.read_csv("App/Data/homeadvantage.csv")

    palette = alt.Scale(domain=['Home Team', 'Away Team'],
                        range=["#5bc0de", "#d9534f"])

    chart = alt.Chart(adv,height=500,width=1000).mark_bar().encode(
        x=alt.X('points:Q', title='Average points'),
        y=alt.Y('team_flag:N', sort='-y', title='', axis=alt.Axis(labels=False)),
        color=alt.Color('team_flag:N', scale=palette, title=''),
        row=alt.Row('league:N', title='',
                    sort=alt.EncodingSortField("points", op='max', order='descending'),
                    header=alt.Header(labelAngle=0, labelAlign='left')),
        tooltip=[alt.Tooltip('points:Q', format='.2f')]
    ).properties(
        height=25
    ).configure_view(
        stroke='transparent'
    ).configure_axis(grid=False).interactive()

    return chart.to_json()



@app.route("/data/points_rating/Leicester")
def getPoints_ratingLei():
    return points_rating("Leicester")

@app.route("/data/points_rating/")
def getPoints_rating():
    return points_rating("")

def leicester():

    points_vs_rating = pd.read_csv("App/Data/points_vs_ratingLeicester.csv")
    df_pointLC = points_vs_rating[points_vs_rating["team_api_id"] == 8197]
    df_pointCH = points_vs_rating[points_vs_rating["team_api_id"] == 8455]

    df_pointLC[
        "comment"] = "All odds were against the Leicester FC, but it ended up winning the league. Good team play, or just luck?"
    df_pointCH["comment"] = "Chelsea was one of the favorites, but it finished 10th in the league."

    all_but_outlier = points_vs_rating[points_vs_rating["team_api_id"] != 8197]
    all_but_outlier = points_vs_rating[points_vs_rating["team_api_id"] != 8455]

    points = alt.Chart(all_but_outlier,height=300,width=500).mark_circle(size=80, opacity=0.3,
                                                    color='grey').encode(alt.X('mean_player_rating',
                                                                               scale=alt.Scale(zero=False),
                                                                               axis=alt.Axis(
                                                                                   title='Team mean player rating')),
                                                                         alt.Y('points_per_game',
                                                                               scale=alt.Scale(zero=False),
                                                                               axis=alt.Axis(title='Points per game')),
                                                                         alt.Color("team_name:N",title="Team Name"),
                                                                         tooltip="team_name").properties(
        title="Season 2015/16, Premier League"
    )
    pointLC = alt.Chart(df_pointLC).mark_circle(size=200, opacity=0.9,
                                                color='green').encode(alt.X('mean_player_rating',
                                                                            scale=alt.Scale(zero=False),
                                                                            axis=alt.Axis(
                                                                                title='Team mean player rating')),
                                                                      alt.Y('points_per_game',
                                                                            scale=alt.Scale(zero=False),
                                                                            axis=alt.Axis(title='Points per game')),
                                                                      alt.Color("team_name:N",title="Team Name"),
                                                                      tooltip=[alt.Tooltip("team_name", title='Team'),
                                                                               alt.Tooltip("comment",
                                                                                           title="Unexpected victory")]).properties(
        title="Season 2015/16, Premier League")

    pointCH = alt.Chart(df_pointCH).mark_circle(size=200, opacity=0.9,
                                                color='red').encode(alt.X('mean_player_rating',
                                                                          scale=alt.Scale(zero=False),
                                                                          axis=alt.Axis(
                                                                              title='Team mean player rating')),
                                                                    alt.Y('points_per_game',
                                                                          scale=alt.Scale(zero=False),
                                                                          axis=alt.Axis(title='Points per game')),
                                                                    alt.Color("team_name:N",title="Team Name"),
                                                                    tooltip=[alt.Tooltip("team_name", title='Team'),
                                                                             alt.Tooltip("comment",
                                                                                         title="A disappointment")]).properties(
                                                                    title="Season 2015/16, Premier League")

    points = points + points.transform_regression("mean_player_rating", "points_per_game").mark_line().transform_fold(
        ["Regression Line"],
        as_=["Regression", ""]).encode(
        color="Regression:N") + pointLC + pointCH

    chart = points.interactive()
    return chart.to_json()


def points_rating(case):
    title =""
    if case == "Leicester":
        return leicester()
    else:
        title = "Season 2010/2011, LIGA BBVA"
        points_vs_rating = pd.read_csv("App/Data/points_vs_ratingNormal.csv")

    points = alt.Chart(points_vs_rating,height=300,width=500).mark_circle(size=80, opacity=0.8,
                                                     color='green').encode(alt.X('mean_player_rating',
                                                                                 scale=alt.Scale(zero=False),
                                                                                 axis=alt.Axis(
                                                                                     title='Team mean player rating')),
                                                                           alt.Y('points_per_game',
                                                                                 scale=alt.Scale(zero=False),
                                                                                 axis=alt.Axis(
                                                                                     title='Points per game')),
                                                                           alt.Color("team_name:N",title="Team Name"),
                                                                           tooltip="team_name").properties(title=title)

    points = points + points.transform_regression("mean_player_rating", "points_per_game").mark_line().transform_fold(
        ["Regression Line"],
        as_=["Regression", ""]).encode(
        color="Regression:N")

    chart = points.interactive()
    return chart.to_json()



@app.route("/data/outlier/")
def outlierStory():
    pl1415 = pd.read_csv("App/Data/2014-PremierLeague.csv")

    # outlier.rename(columns={"team_name": "Team Name"})
    df_pointLC1415 = pl1415[pl1415["team_api_id"] == 8197]

    all_but_LC1415 = pl1415[pl1415["team_api_id"] != 8197]

    points1415 = alt.Chart(all_but_LC1415).mark_circle(size=80, opacity=0.5  # , color='grey'
                                                       ).encode(alt.X('mean_player_rating',
                                                                      scale=alt.Scale(zero=False),
                                                                      axis=alt.Axis(title='Team mean player rating')),
                                                                alt.Y('points_per_game',
                                                                      scale=alt.Scale(zero=False),
                                                                      axis=alt.Axis(title='Points per game')),
                                                                color=alt.Color('team_name',
                                                                                legend=alt.Legend(title="Team Name")),
                                                                tooltip="team_name").properties(
        title="Premier League, Season 2014/15"
    )

    pointLC1415 = alt.Chart(df_pointLC1415).mark_circle(size=120, opacity=1,
                                                        color='red').encode(alt.X('mean_player_rating',
                                                                                  scale=alt.Scale(zero=False),
                                                                                  axis=alt.Axis(
                                                                                      title='Team mean player rating')),
                                                                            alt.Y('points_per_game',
                                                                                  scale=alt.Scale(zero=False),
                                                                                  axis=alt.Axis(
                                                                                      title='Points per game')),
                                                                            # color=alt.Color('team_name'),
                                                                            tooltip=[
                                                                                alt.Tooltip("team_name", title='Team'),
                                                                                # alt.Tooltip("comment", title="Unexpected victory")
                                                                                ]).properties(title="Premier League, Season 2014/15")
    text1415a = alt.Chart({'values': [{'x': 78, 'y': 1.2}]}).mark_text(
        text='The Leicester finished 14th,'
        # , angle=346
    ).encode(
        x='x:Q', y='y:Q'
    )

    text1415b = alt.Chart({'values': [{'x': 78.1, 'y': 1.1}]}).mark_text(
        text='barely escaping relegation...'
        # , angle=346
    ).encode(
        x='x:Q', y='y:Q'
    )

    return (points1415.transform_regression("mean_player_rating", "points_per_game").mark_line().transform_fold(
        ["Regression line"], as_=["Regression", "y"]).encode(alt.Color("Regression:N"))
             + points1415.interactive()
             + pointLC1415.interactive()
             + text1415a + text1415b).to_json()


@app.route("/data/outlier1516/")
def outlierStory2015():
    pl1516 = pd.read_csv("App/Data/2015-PremierLeague.csv")

    # outlier.rename(columns={"team_name": "Team Name"})
    df_pointLC1516 = pl1516[pl1516["team_api_id"] == 8197]

    # df_pointLC["comment"] = "All odds were againts the LC, but it ended up winning the league. Good team play, or just luck?"

    all_but_LC1516 = pl1516[pl1516["team_api_id"] != 8197]

    points1516 = alt.Chart(all_but_LC1516).mark_circle(size=80, opacity=0.5  # , color='grey'
                                                       ).encode(alt.X('mean_player_rating',
                                                                      scale=alt.Scale(zero=False),
                                                                      axis=alt.Axis(title='Team mean player rating')),
                                                                alt.Y('points_per_game',
                                                                      scale=alt.Scale(zero=False),
                                                                      axis=alt.Axis(title='Points per game')),
                                                                color=alt.Color('team_name',
                                                                                legend=alt.Legend(title="Team Name")),
                                                                tooltip="team_name").properties(
        title="Premier League, Season 2015/16"
    )

    pointLC1516 = alt.Chart(df_pointLC1516).mark_circle(size=120, opacity=1,
                                                        color='green').encode(alt.X('mean_player_rating',
                                                                                    scale=alt.Scale(zero=False),
                                                                                    axis=alt.Axis(
                                                                                        title='Team mean player rating')),
                                                                              alt.Y('points_per_game',
                                                                                    scale=alt.Scale(zero=False),
                                                                                    axis=alt.Axis(
                                                                                        title='Points per game')),
                                                                              # color=alt.Color('team_name'),
                                                                              tooltip=[alt.Tooltip("team_name",
                                                                                                   title='Team'),
                                                                                       # alt.Tooltip("comment", title="Unexpected victory")
                                                                                       ]).properties(
        title="Premier League, Season 2015/16")

    text1516 = alt.Chart({'values': [{'x': 73, 'y': 2}]}).mark_text(
        text='Here is our miracle winner, the Leicester City!'
        # , angle=346
    ).encode(
        x='x:Q', y='y:Q'
    )

    # for regression to work, you have to add interaction to the final plot (not before regression)
    return (points1516.transform_regression("mean_player_rating", "points_per_game").mark_line().transform_fold(
        ["Regression line"], as_=["Regression", "y"]).encode(alt.Color("Regression:N"))
             + points1516.interactive()
             + pointLC1516.interactive()
             + text1516).to_json()


@app.route("/data/comparePoints/<name>")
def comparePoints(name):
    if name == "EFL":
        dataframe = pd.read_csv("App/Data/LeicesterEFL.csv")
    elif name == "1415":
        dataframe = pd.read_csv("App/Data/ChelseaLei.csv")
    else:
        pass
    return comparePointsChart(dataframe)


def comparePointsChart(dataframe):

    # flcc = pd.read_csv("App/Data/LeicesterEFL.csv")

    line = alt.Chart(dataframe).mark_line().encode(
        x=alt.X('Matches', title='Match'),
        y=alt.Y('value:Q', title='Points per game'),
        color=alt.Color('variable:N', title="Season")
    )

    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['Matches'], empty='none')

    selectors = alt.Chart(dataframe).mark_point().encode(
        x='Matches',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    text = line.mark_text(align='right', dx=-15, dy=-15).encode(
        text=alt.condition(nearest, 'value:Q', alt.value(' '))
    )

    chart = alt.layer(line, selectors, points, text).configure_axis(
        grid=False
    ).configure_point(
        size=100
    ).configure_line(
        size=4
    ).configure_view(
        stroke='').properties(width=700, height=300).interactive()

    return chart.to_json()

# render cars.html page
@app.route("/dashboard")
def statistics():
    form = selectYear(request.form)
    selectForm = chartSelect(request.form)

    return render_template("dashboard.html",form=form,selectForm=selectForm)


if __name__ == '__main__':
    app.run()
