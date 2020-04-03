from flask import Flask
import pandas as pd
import pygal
from pygal import Config
import os, ssl


app = Flask(__name__)

@app.route('/age_range.svg')
def plot_age_range():
    #create a df
    df_age = pd.DataFrame.from_dict({'age_range':['< 20','20s', '30s', '40s',
                                                  '50s', '60s', '70s','80+'],
                                 'cases': [6,35,28,54,69,77,46,29]})
    # add up the total cases and find % of total in each age range
    total_count = df_age.cases.sum()
    df_age['percent_of_tot'] = df_age.cases/total_count*100
    df_age = df_age.round({'percent_of_tot':1})

    # create a bar chart of the age range data
    bar_chart = pygal.Bar(x_label_rotation=20,
                      show_legend=False,
                      y_title='Percent of Cases (%)',
                      x_title='Age Group')
    bar_chart.title = 'Case Distribution by Patient Age'
    bar_chart.x_labels = df_age.age_range
    bar_chart.add('% of Cases', df_age.percent_of_tot.to_list())

    return bar_chart.render_response()

@app.route('/case_status.svg')
def plot_case_status():
    # import data from the NY Times GitHub repo
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context
    url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
    df = pd.read_csv(url, error_bad_lines=False)

    # make a df for just the Maine data
    df_maine = df[df.state == 'Maine']

    # find the total cases, deaths for each day
    df_state_tot = df_maine.groupby('date').sum()

    # add a recovered column from the Press Herald data
    df_state_tot['recovered']=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,16,24,36,41,41,68,80]

    #calculate active case counts
    df_state_tot['active_cases'] = df_state_tot.cases - df_state_tot.deaths - df_state_tot.recovered

    # plot the daily total cases, deaths, and recovered
    bar_chart = pygal.StackedBar(x_label_rotation=20, show_minor_x_labels=False)
    bar_chart.title = 'Maine COVID-19 Cases by Status'
    bar_chart.x_labels = df_state_tot.index.values.tolist()
    bar_chart.x_labels_major = df_state_tot.index.values.tolist()[0::3]

    bar_chart.add('Active Cases', df_state_tot.active_cases.values.tolist())
    bar_chart.add('Deaths', df_state_tot.deaths.values.tolist())
    bar_chart.add('Recovered Cases', df_state_tot.recovered.values.tolist())

    return bar_chart.render_response()
