from flask import Flask
import pandas as pd
import pygal
from pygal import Config
import os, ssl
import numpy as np
from pygal.style import Style


app = Flask(__name__)

def import_nytimes_data():
    ''' Import data from the NY Times GitHub repo'''

    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context
    url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
    df = pd.read_csv(url, error_bad_lines=False)
    return df

def create_maine_df():
    ''' Make a df for just the Maine data from the NY Times'''

    df = import_nytimes_data()
    # make a df for the NY Times Maine data
    df_maine = df[df.state == 'Maine']
    return df_maine

def create_maine_daily_totals_df():
    ''' Create a df with total cases and deaths in Maine for each day '''

    df_maine = create_maine_df()
    # find the total cases, deaths for each day
    df_state_tot = df_maine.groupby('date').sum()
    return df_state_tot

def create_maine_most_recent_df():
    # make a df for the Maine data from the NY Times
    df_maine = create_maine_df()
    # make a df for the most recent day's data
    df_maine_today = df_maine[df_maine.date == df_maine.date.max()]
    # sort the df by case count
    df_maine_today.sort_values(by=['cases'], ascending=False, inplace=True)

    return df_maine_today

def create_population_df():
    # make a dataframe of county population data
    # (source: https://data.census.gov/cedsci/profile?g=0500000US23005&q=Cumberland)
    population_data = {'Cumberland': 290944,
                       'York':203102,
                       'Oxford':57325,
                       'Sagadahoc':35277,
                       'Androscoggin':107444,
                       'Lincoln':34067,
                       'Kennebec':121545,
                       'Franklin':30019,
                       'Knox':39823,
                       'Waldo':39418,
                       'Somerset':50710,
                       'Hancock':54541,
                       'Washington':31694,
                       'Piscataquis':16877,
                       'Penobscot':151748,
                       'Aroostook': 68269,
                       'Unknown':np.nan}
    df_population = pd.DataFrame.from_dict(population_data, orient='index',columns=['population'])

    return df_population

@app.route('/age_range.svg')
def plot_age_range():
    #create a df
    df_age = pd.DataFrame.from_dict({'age_range':['< 20','20s', '30s', '40s',
                                                  '50s', '60s', '70s','80+'],
                                 'cases': [9,43,35,67,87,96,58,37]})
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
    # create a df with total cases and deaths in Maine for each day
    df_state_tot = create_maine_daily_totals_df()

    # add a recovered column from the Press Herald data
    df_state_tot['recovered']=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,16,24,36,41,41,68,80, 94]
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

@app.route('/new_cases_maine.svg')
def plot_new_cases():
    # make a df with the total cases, deaths for each day
    df_state_tot = create_maine_daily_totals_df()

    # calculate new cases per day
    df_state_tot['new_cases'] = df_state_tot.cases.diff()
    df_state_tot['new_cases'][0] = 1

    # plot new cases per day
    bar_chart = pygal.Bar(x_label_rotation=20,
                      show_minor_x_labels=False,
                      show_legend=False,
                      y_title = 'Number of New Cases',
                      x_title = 'Day')
    bar_chart.title = 'Daily New COVID-19 Cases in Maine'
    bar_chart.x_labels = df_state_tot.index.values.tolist()
    bar_chart.x_labels_major = df_state_tot.index.values.tolist()[0::3]
    bar_chart.add('Number of New Cases', df_state_tot.new_cases.to_list())

    return bar_chart.render_response()

@app.route('/total_deaths.svg')
def plot_deaths():
    # make a df with the total cases, deaths for each day
    df_state_tot = create_maine_daily_totals_df()

    # plot death data
    bar_chart = pygal.Bar(x_label_rotation=20,
                          show_minor_x_labels=False,
                          show_legend=False,
                          y_title='Total Number of Deaths')
    bar_chart.title = 'Total COVID-19 Deaths in Maine'
    dates = df_state_tot.index.values.tolist()
    bar_chart.x_labels = dates
    bar_chart.x_labels_major = dates[0::3]

    bar_chart.add('Total Deaths', df_state_tot.deaths.values.tolist())

    return bar_chart.render_response()

@app.route('/cases_by_county.svg')
def plot_current_cases_by_county():
    # make a df for the most recent day's data
    df_maine_today = create_maine_most_recent_df()

    # plot the data
    bar_chart = pygal.Bar(x_label_rotation=20,
                          show_legend=False,
                          y_title='Number of Cases',
                          x_title='County')
    title_text = 'COVID-19 Cases by County' + ' (' + str(df_maine_today.date.max()) + ')'
    bar_chart.title = title_text
    bar_chart.x_labels = df_maine_today.county.to_list()
    bar_chart.add('Cases', df_maine_today.cases.to_list())

    return bar_chart.render_response()

@app.route('/cases_per_capita.svg')
def plot_county_cases_per_capita():
    # make a df of the population of Maine counties based on US Census Data
    df_population = create_population_df()
    # make a df for the most recent day's NY Times data for Maine
    df_maine_today = create_maine_most_recent_df()
    # add the population data to the NY Times Data
    df_maine_today = df_maine_today.merge(df_population, left_on='county', right_index=True)
    # calculate cases per 100,000 residents
    df_maine_today['cases_per_hundred_thousand'] = df_maine_today.cases/ \
                                                    (df_maine_today.population/100000)
    df_maine_today = df_maine_today.round({'cases_per_hundred_thousand':0})

    # plot the data
    bar_chart = pygal.Bar(x_label_rotation=20,
                          show_legend=False,
                          y_title='Cases per 100,000 Residents',
                          x_title='County')
    title_text = 'COVID-19 Cases per 100,000 Residents' + ' (' + \
                  str(df_maine_today.date.max()) + ')'
    bar_chart.title = title_text
    bar_chart.x_labels = df_maine_today.county.to_list()
    bar_chart.add('Cases per 100,000 People', df_maine_today.cases_per_hundred_thousand.to_list())

    return bar_chart.render_response()
