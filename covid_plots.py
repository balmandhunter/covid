from flask import Flask
import pandas as pd
import pygal
from pygal import Config
from pygal.style import Style
import os, ssl
import numpy as np
from pygal.style import Style

from middleware import sizes

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
    ''' make a df for the Maine data from the NY Times'''
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


def create_days_to_double_data(df, days_to_double):
    cases= [1]
    n_days = len(df.date.unique())
    d = range(1,len(df.date.unique()))
    for day in d:
        cases.append(round(2**(day/days_to_double),2))
    return cases


def plot_county_lines(df_maine, line_chart):
    for county in df_maine.county.unique():
        if len(list(df_maine.date.unique())) == len(df_maine[df_maine.county==county].cases):
            case_data = df_maine[df_maine.county==county].cases
        else:
            len_diff = len(list(df_maine.date.unique())) - \
                        len(df_maine[df_maine.county==county].cases)
            case_data = df_maine[df_maine.county==county].cases.to_list()
            case_data = [0]*len_diff + case_data
        line_chart.add(county, case_data, dots_size=1.5)


def append_recovered_data(df):
    recovered = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,16,24,36,41,41,68,80,94,113,140]
    while len(recovered) < len(df):
        recovered.append(np.nan)
    df['recovered'] = recovered
    return df


def get_hospitalized(df):
    hospitalized=[None,None,None,None,None,None,None,None,None,None,49,57,63,68,75,83]
    hosp_dates = ['2020-03-20', '2020-03-21','2020-03-22','2020-03-23','2020-03-24',
                  '2020-03-25','2020-03-26','2020-03-27','2020-03-28','2020-03-29',
                  '2020-03-30','2020-03-31','2020-04-01','2020-04-02','2020-04-03',
                  '2020-04-04']

    return hospitalized, hosp_dates


def find_occupied_assets(the_dict, total_asset, available_asset, return_col_name='occupied'):
    occupied_asset = []
    for idx in range(0, len(the_dict['date'])):
        if the_dict[total_asset][idx] is not None and the_dict[available_asset][idx] is not None:
            occupied_asset.append(the_dict[total_asset][idx] - the_dict[available_asset][idx])
        else:
            occupied_asset.append(None)

    the_dict[return_col_name] = occupied_asset
    return the_dict


def find_total_vent_including_alt(the_dict):
    total_vent_including_alt = []
    for idx in range(0, len(the_dict['date'])):
        if the_dict['total_ventilators'][idx] is not None and the_dict['alternative_ventilators'][idx] is not None:
            total_vent_including_alt.append(the_dict['total_ventilators'][idx] + the_dict['alternative_ventilators'][idx])
        else:
            total_vent_including_alt.append(None)

    the_dict['total_vent_including_alt'] = total_vent_including_alt
    return the_dict


def large_style_bar():
    custom_style = Style(
        colors=['#3F51B5', '#F44336', '#009688'],
        title_font_size=18,
        label_font_size=14,
        major_label_font_size=14,
        legend_font_size=14
    )
    return custom_style

def small_style_bar():
    custom_style = Style(
        colors=['#3F51B5', '#F44336', '#009688'],
        title_font_size=30,
        label_font_size=24,
        major_label_font_size=24,
        legend_font_size=24
    )
    return custom_style


def create_hospital_assets_dict():
    hosp_assets_dict = {'date':['2020-03-20','2020-03-21', '2020-03-22', '2020-03-23','2020-03-24',
                            '2020-03-25','2020-03-26','2020-03-27','2020-03-28','2020-03-29',
                            '2020-03-30','2020-03-31', '2020-04-01','2020-04-02','2020-04-03'],
                         'total_icu_beds':[135, None, None, None, None,
                                           151, 151, 164, None, None,
                                           176, 190, 272, 285, 289],
                         'available_icu_beds': [56, None, None, None, 77,
                                                83, 86, 86, None, None,
                                                92, 90, 124, 122, 110],
                         'total_ventilators':[291, None, None, None, None,
                                              306, 307, 308, None, None,
                                              309, 330, 348, 334, 324],
                         'available_ventilators':[218, None, None, None, 248,
                                                  248, 250, 247, None, None,
                                                  253, 262, 271, 266, 267],
                         'alternative_ventilators':[None, None, None, None, None,
                                                    None, None, 58, None, None,
                                                    87, 89, 128, 186, 199],
                         'respiratory_therapists':[None, None, None, None, 84,
                                                   88, None, None, None, None,
                                                   None, None, None, None, 127]
                        }
    # Calculate the number of occupied ICU Beds
    hosp_assets_dict = find_occupied_assets(hosp_assets_dict, 'total_icu_beds', 'available_icu_beds',
                                            return_col_name='occupied_icu_beds')
    hosp_assets_dict = find_occupied_assets(hosp_assets_dict, 'total_ventilators', 'available_ventilators',
                                            return_col_name='occupied_ventilators')
    hosp_assets_dict = find_total_vent_including_alt(hosp_assets_dict)

    return hosp_assets_dict


@app.route('/age_range.svg')
def plot_age_range():
    #create a df
    df_age = pd.DataFrame.from_dict({'age_range':['< 20','20s', '30s', '40s',
                                                  '50s', '60s', '70s','80+'],
                                 'cases': [11,43,40,80,93,101,64,38]})
    # add up the total cases and find % of total in each age range
    total_count = df_age.cases.sum()
    df_age['percent_of_tot'] = df_age.cases/total_count*100
    df_age = df_age.round({'percent_of_tot':1})

    # create a bar chart of the age range data
    bar_chart = pygal.Bar(x_label_rotation=20,
                          show_legend=False,
                          y_title='Percent of Cases (%)',
                          x_title='Age Group')
    # title_text = 'Case Distribution by Patient Age' + ' (' + str(df_maine_today.date.max()) + ')'
    bar_chart.title = 'Case Distribution by Patient Age (April 5, 2020)'
    bar_chart.x_labels = df_age.age_range
    bar_chart.add('% of Cases', df_age.percent_of_tot.to_list())

    return bar_chart.render_response()

@app.route('/case_status.svg')
@sizes
def plot_case_status(size):
    if size == 'small':
        custom_style = small_style_bar()
        date_skip = 4
        date_rot = 30
        leg_pos = True
        space_sz = 30
    else:
        custom_style = large_style_bar()
        date_rot = 20
        date_skip = 3
        leg_pos = False
        space_sz = 18

    # create a df with total cases and deaths in Maine for each day
    df_state_tot = create_maine_daily_totals_df()

    # add a recovered column from the Press Herald data
    df_state_tot = append_recovered_data(df_state_tot)
    df_state_tot['active_cases'] = df_state_tot.cases - df_state_tot.deaths - df_state_tot.recovered

    # plot the daily total cases, deaths, and recovered
    bar_chart = pygal.StackedBar(style=custom_style,
                                 x_label_rotation=date_rot,
                                 show_minor_x_labels=False,
                                 legend_at_bottom=leg_pos,
                                 spacing=space_sz,
                                 legend_at_bottom_columns=2
                                 )
    bar_chart.title = 'Maine COVID-19 Cases by Status'
    bar_chart.x_labels = df_state_tot.index.values.tolist()
    bar_chart.x_labels_major = df_state_tot.index.values.tolist()[0::date_skip]

    bar_chart.add('Active Cases', df_state_tot.active_cases.values.tolist())
    bar_chart.add('Deaths', df_state_tot.deaths.values.tolist())
    bar_chart.add('Recovered Cases', df_state_tot.recovered.values.tolist())

    return bar_chart.render_response()


@app.route('/new_cases_maine.svg')
@sizes
def plot_new_cases(size):
    if size == 'small':
        custom_style = small_style_bar()
        custom_style.title_font_size = 26
        date_skip = 5
    else:
        custom_style = large_style_bar()
        date_skip = 3

    # make a df with the total cases, deaths for each day
    df_state_tot = create_maine_daily_totals_df()

    # calculate new cases per day
    df_state_tot['new_cases'] = df_state_tot.cases.diff()
    df_state_tot['new_cases'][0] = 1

    # plot new cases per day
    bar_chart = pygal.Bar(style=custom_style,
                          x_label_rotation=20,
                          show_minor_x_labels=False,
                          show_legend=False,
                          y_title = 'Number of New Cases')
    bar_chart.title = 'New COVID-19 Cases in Maine per Day'
    bar_chart.x_labels = df_state_tot.index.values.tolist()
    bar_chart.x_labels_major = df_state_tot.index.values.tolist()[0::date_skip]
    bar_chart.add('Number of New Cases', df_state_tot.new_cases.to_list())

    return bar_chart.render_response()

@app.route('/total_deaths.svg')
@sizes
def plot_deaths(size):
    if size == 'small':
        custom_style = small_style_bar()
        custom_style.title_font_size = 26
        date_skip = 5
    else:
        custom_style = large_style_bar()
        date_skip = 3

    # make a df with the total cases, deaths for each day
    df_state_tot = create_maine_daily_totals_df()

    # plot death data
    bar_chart = pygal.Bar(style=custom_style,
                          x_label_rotation=20,
                          show_minor_x_labels=False,
                          show_legend=False,
                          y_title='Total Number of Deaths')
    bar_chart.title = 'Total COVID-19 Deaths in Maine'
    dates = df_state_tot.index.values.tolist()
    bar_chart.x_labels = dates
    bar_chart.x_labels_major = dates[0::date_skip]

    bar_chart.add('Total Deaths', df_state_tot.deaths.values.tolist())

    return bar_chart.render_response()

@app.route('/new_deaths.svg')
@sizes
def plot_new_deaths(size):
    if size == 'small':
        custom_style = small_style_bar()
        custom_style.title_font_size = 26
        date_skip = 5
    else:
        custom_style = large_style_bar()
        date_skip = 3

    # make a df with the total cases, deaths for each day
    df_state_tot = create_maine_daily_totals_df()

    df_state_tot['new_deaths'] = df_state_tot.deaths.diff()
    df_state_tot['new_deaths'][0] = 0

    bar_chart = pygal.Bar(x_label_rotation=20,
                      show_minor_x_labels=False,
                      show_legend=False,
                      y_title = 'Number of New Deaths')
    bar_chart.title = 'New COVID-19 Deaths in Maine per Day'
    dates = df_state_tot.index.values.tolist()
    bar_chart.x_labels = dates
    bar_chart.x_labels_major = dates[0::date_skip]
    bar_chart.add('Number of New Deaths', df_state_tot.new_deaths.to_list())

    return bar_chart.render_response()

@app.route('/cases_by_county.svg')
@sizes
def plot_current_cases_by_county(size):
    if size == 'small':
        custom_style = small_style_bar()
        custom_style.title_font_size = 26
        custom_style.label_font_size = 18
        x_rot = 40
    else:
        custom_style = large_style_bar()
        x_rot=20

    # make a df for the most recent day's data
    df_maine_today = create_maine_most_recent_df()

    # plot the data
    bar_chart = pygal.Bar(style=custom_style,
                          x_label_rotation=x_rot,
                          show_legend=False,
                          y_title='Number of Cases',
                          x_title='County')
    title_text = 'COVID-19 Cases by County' + ' (' + str(df_maine_today.date.max()) + ')'
    bar_chart.title = title_text
    bar_chart.x_labels = df_maine_today.county.to_list()
    bar_chart.add('Cases', df_maine_today.cases.to_list())

    return bar_chart.render_response()


@app.route('/cases_per_ten_thousand_res.svg')
@sizes
def plot_cases_per_ten_thousand_res(size):
    if size == 'small':
        custom_style = small_style_bar()
        custom_style.title_font_size = 24
        custom_style.label_font_size = 18
        x_rot=40
    else:
        custom_style = large_style_bar()
        date_skip = 3
        x_rot=30

    # make a df of the population of Maine counties based on US Census Data
    df_population = create_population_df()
    # make a df for the most recent day's NY Times data for Maine
    df_maine_today = create_maine_most_recent_df()
    # add the population data to the NY Times Data
    df_maine_today = df_maine_today.merge(df_population, left_on='county', right_index=True)
    # calculate cases per 100,000 residents
    df_maine_today['cases_per_ten_thousand'] = df_maine_today.cases/ \
                                                    (df_maine_today.population/10000)
    df_maine_today = df_maine_today.round({'cases_per_ten_thousand':1})
    # Drop the Unknown county row
    unknown_idx = df_maine_today[df_maine_today.county=='Unknown'].index
    df_maine_today = df_maine_today.drop(labels=unknown_idx, axis=0)

    # plot the data
    bar_chart = pygal.Bar(style=custom_style,
                          x_label_rotation=x_rot,
                          show_legend=False,
                          y_title='Cases per 10,000 People',
                          x_title='County')
    title_text = 'COVID-19 Cases per 10,000 Residents' + ' (' + \
                  str(df_maine_today.date.max()) + ')'
    bar_chart.title = title_text
    bar_chart.x_labels = df_maine_today.county.to_list()
    bar_chart.add('Cases per 10,000 Residents', df_maine_today.cases_per_ten_thousand.to_list())

    return bar_chart.render_response()



def get_custom_style(size):
    if size=='small':
        custom_style = Style(
            colors=['#85144B', '#111111', '#7FDBFF', '#39CCCC', '#3D9970', '#2ECC40', '#01FF70',
                    '#FFDC00', '#FF851B', '#FF4136', '#F012BE', '#B10DC9', '#00008b', '#0074D9',
                    '#85144B', '#7FDBFF', '#6e6e6e', '#9e9e9e', '#dbdbdb'],
            label_font_size=18,
            major_guide_stroke_dasharray= '1.5,1.5',
            title_font_size=24,
            major_label_font_size=20,
            legend_font_size=18
        )
    else:
        custom_style = Style(
            colors=['#85144B', '#111111', '#7FDBFF', '#39CCCC', '#3D9970', '#2ECC40', '#01FF70',
                    '#FFDC00', '#FF851B', '#FF4136', '#F012BE', '#B10DC9', '#00008b', '#0074D9',
                    '#85144B', '#7FDBFF', '#6e6e6e', '#9e9e9e', '#dbdbdb'],
            label_font_size=12,
            major_guide_stroke_dasharray= '1.5,1.5',
            title_font_size=18,
            major_label_font_size=14,
            legend_font_size=13
        )
    return custom_style


def line_config(size):
    if size=='small':
        config = Config()
        custom_style = get_custom_style(size)
        config.style=custom_style
        config.x_label_rotation=40
        config.show_minor_x_labels=False
        config.y_labels_major_every=3
        config.show_minor_y_labels=False
        config.truncate_legend=-1
    else:
        config = Config()
        custom_style = get_custom_style(size)
        config.style=custom_style
        config.x_label_rotation=20
        config.show_minor_x_labels=False
        config.y_labels_major_every=3
        config.show_minor_y_labels=False
        config.truncate_legend=-1
    return config


@app.route('/growth_by_county.svg')
@sizes
def plot_growth_by_county(size):
    df_maine = create_maine_df()
    config = line_config(size)
    dates = list(df_maine.date.unique())
    if size == 'small':
        date_skip = 5
        the_height = 800
        the_width = 600
        leg_pos = True
        space_sz = 26
    else:
        date_skip = 5
        the_height = 500
        the_width = 700
        leg_pos = False
        space_sz = 14

    line_chart = pygal.Line(config,
                            y_title='Number of Cases',
                            height=the_height,
                            width=the_width,
                            legend_at_bottom=leg_pos,
                            spacing=space_sz,
                            legend_at_bottom_columns=2)
    line_chart.title = 'COVID-19 Case Growth by County'
    line_chart.x_labels = list(df_maine.date.unique())
    line_chart.x_labels_major = list(df_maine.date.unique())[0::date_skip]
    #add a line for each county
    plot_county_lines(df_maine, line_chart)

    return line_chart.render_response()


@app.route('/growth_by_county_log.svg')
@sizes
def plot_growth_by_county_log(size):
    df_maine = create_maine_df()
    config = line_config(size)
    dates = list(df_maine.date.unique())
    if size == 'small':
        date_skip = 5
        the_height = 1000
        the_width = 600
        leg_pos = True
        space_sz = 26
    else:
        date_skip = 5
        the_height = 500
        the_width = 800
        leg_pos = False
        space_sz = 14

    # Import the data
    df_maine = create_maine_df()
    # Setup Configuration
    config = line_config(size)
    # Plot the data
    line_chart = pygal.Line(config,
                        y_title='Cases',
                        logarithmic=True,
                        height=the_height,
                        width=the_width,
                        legend_at_bottom=leg_pos,
                        spacing=space_sz,
                        legend_at_bottom_columns=1
                        )
    line_chart.title = 'COVID-19 Case Growth by County (log scale)'
    line_chart.x_labels = list(df_maine.date.unique())
    line_chart.x_labels_major = list(df_maine.date.unique())[0::date_skip]
    #add a line for each county
    plot_county_lines(df_maine, line_chart)
    # Set the stoke style for the reference lines and plot them
    ref_style = stroke_style={'width':2.5}
    line_chart.add('Cases Double every 3 Days', create_days_to_double_data(df_maine, 3),
                  stroke_style=ref_style, dots_size=1)
    line_chart.add('Cases Double every 5 Days', create_days_to_double_data(df_maine, 5),
                   stroke_style=ref_style, dots_size=1)
    line_chart.add('Cases Double every Week', create_days_to_double_data(df_maine, 7),
                   stroke_style=ref_style, dots_size=1)

    return line_chart.render_response()


@app.route('/hospitalization.svg')
def plot_hospitalization():
    # make a df with the total cases, deaths for each day
    df_state_tot = create_maine_daily_totals_df()
    hospitalized, hosp_dates = get_hospitalized(df_state_tot)

    custom_style = Style(
        colors=['#08519c', '#3182bd'],
        label_font_size=14,
        major_guide_stroke_dasharray= '1.5,1.5'
    )

    line_chart = pygal.Line(style=custom_style,
                            include_x_axis=True,
                            x_label_rotation=20,
                            show_minor_x_labels=False,
                            y_labels_major_every=2,
                            show_minor_y_labels=False,
                            truncate_legend=-1,
                            x_title = 'Date')
    line_chart.title = 'Total Patients Ever Hospitalized for COVID-19 in Maine'
    line_chart.x_labels = hosp_dates
    line_chart.x_labels_major = hosp_dates[0::2]
    line_chart.add('Total Hospitalized', hospitalized,
                   stroke_style={'dasharray': '3, 6', 'width':2.5})

    return line_chart.render_response()


@app.route('/ventilators.svg')
def plot_ventilators():
    hosp_assets_dict = create_hospital_assets_dict()

    custom_style = Style(
        colors=['#08519c', '#3182bd', '#6baed6'],
        label_font_size=14,
        major_guide_stroke_dasharray= '1.5,1.5',
        legend_font_size= 10
    )

    line_chart = pygal.Line(style=custom_style,
                            dots_size=2,
                            x_label_rotation=20,
                            show_minor_x_labels=False,
                            y_labels_major_every=2,
                            show_minor_y_labels=False,
                            width=750,
                            height=400,
                            truncate_legend=-1
                           )

    line_chart.title = 'Statewide Ventilator Availablity'
    line_chart.x_labels = hosp_assets_dict['date']
    line_chart.x_labels_major = hosp_assets_dict['date'][0::3]

    line_chart.add('Total Ventilators (including alternative)', hosp_assets_dict['total_vent_including_alt'],
                   stroke_style={'width':2.5}, show_dots=1, dots_size=1)
    line_chart.add('Total Traditional Ventilators', hosp_assets_dict['total_ventilators'],
                   stroke_style={'width':2.5}, show_dots=1, dots_size=1)
    line_chart.add('Occupied Ventilators', hosp_assets_dict['occupied_ventilators'],
                  stroke_style={'dasharray': '3, 6', 'width':2.5})

    return line_chart.render_response()


@app.route('/icu_beds.svg')
def plot_icu_beds():
    hosp_assets_dict = create_hospital_assets_dict()

    custom_style = Style(
        colors=['#08519c', '#3182bd'],
        label_font_size=14,
        major_guide_stroke_dasharray= '1.5,1.5'
    )

    line_chart = pygal.Line(style=custom_style,
                            dots_size=2.5,
                            x_label_rotation=20,
                            truncate_legend=-1,
                            show_minor_x_labels=False,
                            y_labels_major_every=2,
                            show_minor_y_labels=False
                            )
    line_chart.title = 'Statewide ICU Bed Availablity'
    line_chart.x_labels = hosp_assets_dict['date']
    line_chart.x_labels_major = hosp_assets_dict['date'][0::3]

    line_chart.add('Total ICU Beds', hosp_assets_dict['total_icu_beds'], stroke_style={'width':2.5},
                   show_dots=1, dots_size=1)
    line_chart.add('Occupied ICU Beds', hosp_assets_dict['occupied_icu_beds'],
                   stroke_style={'dasharray': '3, 6', 'width':2.5})

    return line_chart.render_response()
