
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


@app.route("/data/best_team/<year>")
def points_team_opp(year):
    year = int(year)
    print("ASDDDDDDDDDDD")

    bigDf = pd.read_csv("App/Data/CumulativeSeasons.csv")

    dfSeason = bigDf[bigDf['season'] == str(year+2000)+"/"+str((year+1)+2000)]


    df = dfSeason.groupby(['result', 'team_long_name']).size()['won'].sort_values(ascending=False)[:5]
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
        column=alt.Column('Team:O')
    ).configure_view(
        stroke='transparent'
    ).interactive()

    return chart.to_json()


# render cars.html page
@app.route("/dashboard")
def statistics():
    form = selectYear(request.form)

    return render_template("dashboard.html",form=form)


if __name__ == '__main__':
    app.run()
