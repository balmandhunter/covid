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

def get_maine_df():
    ''' Make a df for just the Maine data from the API'''
    df_maine = pd.read_csv(
        'http://mecovid19data.almandhunter.com/api/v0/countydata.csv?')
    return df_maine


def combine_counties(df_maine):
    ''' Create a df with total cases and deaths in Maine for each day '''
    # find the total cases, deaths for each day
    df_state_tot = df_maine.groupby('date').sum()
    return df_state_tot


def get_most_recent_data():
    ''' Make a df for the most recent Maine data from the data API'''
    df_maine_today = pd.read_csv(
        'http://mecovid19data.almandhunter.com/api/v0/countydata.csv?latest')
    # sort the df by case count
    df_maine_today.sort_values(by=['confirmed'], ascending=False, inplace=True)
    return df_maine_today


def create_population_df():
    # make a dataframe of county population data
    # (source: https://data.census.gov/cedsci/profile?g=0500000US23005&q=Cumberland)
    population_data = {'county':['Cumberland', 'York', 'Oxford', 'Sagadahoc', 'Androscoggin',
                                 'Lincoln', 'Kennebec', 'Franklin', 'Knox', 'Waldo', 'Somerset',
                                 'Hancock', 'Washington', 'Piscataquis', 'Penobscot', 'Aroostook',
                                 'Unknown'],
                       'population':[290944, 203102,  57325,  35277, 107444,  34067, 121545,
                                     30019,  39823,  39418,  50710,  54541,  31694,  16877,
                                     151748,  68269, np.nan],
                       'county_area_sq_mile':[835.5, 990.5, 2076.3, 253.9, 467.8,
                                    455.7, 867.3, 1696.5, 365, 729.7, 3923.3,
                                    1586.6, 2562, 3959.9, 3396.3, 6669.3,
                                    np.nan]}
    df_population = pd.DataFrame.from_dict(population_data)
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
        if county != 'Unknown':
            if len(list(df_maine.date.unique())) == len(df_maine[df_maine.county==county].confirmed):
                case_data = df_maine[df_maine.county==county].confirmed
            else:
                len_diff = len(list(df_maine.date.unique())) - \
                            len(df_maine[df_maine.county==county].confirmed)
                case_data = df_maine[df_maine.county==county].confirmed.to_list()
                case_data = [0]*len_diff + case_data
            # dd the data for each county tp the plot
            line_chart.add(county, case_data, stroke_style={'width':1.75})


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
        label_font_size=18,
        major_label_font_size=18,
        legend_font_size=16
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
                            '2020-03-30','2020-03-31', '2020-04-01','2020-04-02','2020-04-03',
                            '2020-04-04', '2020-04-05', '2020-04-06', '2020-04-07', '2020-04-08',
                            '2020-04-09','2020-04-10', '2020-04-11', '2020-04-12', '2020-04-13',
                            '2020-04-14', '2020-04-15', '2020-04-16', '2020-04-17', '2020-04-18',
                            '2020-04-19', '2020-04-20'],
                         'total_icu_beds':[135, None, None, None, None,
                                           151, 151, 164, None, None,
                                           176, 190, 272, 285, 289,
                                           None, None, 300, None, 305,
                                           308, None, None, None, 314,
                                           None, None, 319, 321, None,
                                           320, 316],
                         'available_icu_beds': [56, None, None, None, 77,
                                                83, 86, 86, None, None,
                                                92, 90, 124, 122, 110,
                                                None, None, 120, None, 154,
                                                149, None, None, None, 158,
                                                163, None, 158, 151, None,
                                                167, 152],
                         'total_ventilators':[291, None, None, None, None,
                                              306, 307, 308, None, None,
                                              309, 330, 348, 334, 324,
                                              None, None, 324, None, 331,
                                              333, None, None, None, 328,
                                              None, None, 344, 344, None,
                                              338, 336],
                         'available_ventilators':[218, None, None, None, 248,
                                                  248, 250, 247, None, None,
                                                  253, 262, 271, 266, 267,
                                                  None, None, 268, None, 282,
                                                  283, None, None, None, 283,
                                                  283, None, 313, 309, None,
                                                  297, 287],
                         'alternative_ventilators':[None, None, None, None, None,
                                                    None, None, 58, None, None,
                                                    87, 89, 128, 186, 199,
                                                    None, None, 199, None, 233,
                                                    232, None, None, None, 234,
                                                    None, None, 240, 240, None,
                                                    369, 369],
                         'respiratory_therapists':[None, None, None, None, 84,
                                                   88, None, None, None, None,
                                                   None, None, None, None, 127,
                                                   None, None, 130, None, None,
                                                   None, None, None, None, None,
                                                   None, None, None, None, None,
                                                   None,None]
                        }
    # Calculate the number of occupied ICU Beds
    hosp_assets_dict = find_occupied_assets(hosp_assets_dict, 'total_icu_beds',
                                            'available_icu_beds',
                                            return_col_name='occupied_icu_beds')
    hosp_assets_dict = find_occupied_assets(hosp_assets_dict, 'total_ventilators',
                                            'available_ventilators',
                                            return_col_name='occupied_ventilators')
    hosp_assets_dict = find_total_vent_including_alt(hosp_assets_dict)

    return hosp_assets_dict


def get_custom_style(size):
    if size=='small':
        custom_style = Style(
            colors=['#85144B', '#111111', '#7FDBFF', '#39CCCC', '#3D9970', '#2ECC40', '#01FF70',
                    '#FFDC00', '#FF851B', '#FF4136', '#F012BE', '#B10DC9', '#00008b', '#0074D9',
                    '#85144B', '#C0C0C0', '#A9A9A9', '#696969'],
            label_font_size=18,
            major_guide_stroke_dasharray= '1.5,1.5',
            title_font_size=24,
            major_label_font_size=20,
            legend_font_size=18,
            stroke_opacity=0.6
        )
    else:
        custom_style = Style(
            colors=['#85144B', '#111111', '#7FDBFF', '#39CCCC', '#3D9970', '#2ECC40', '#01FF70',
                    '#FFDC00', '#FF851B', '#FF4136', '#F012BE', '#B10DC9', '#00008b', '#0074D9',
                    '#85144B', '#C0C0C0', '#A9A9A9', '#696969'],
            label_font_size=12,
            major_guide_stroke_dasharray= '1.5,1.5',
            title_font_size=18,
            major_label_font_size=14,
            legend_font_size=13,
            stroke_opacity=0.6
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


def get_custom_style_assets(size):
        if size=='small':
            custom_style = Style(
                colors=['#08519c', '#3182bd'],
                label_font_size=18,
                major_guide_stroke_dasharray= '1.5,1.5',
                title_font_size=26,
                major_label_font_size=24,
                legend_font_size=24
            )
        else:
            custom_style = Style(
                colors=['#08519c', '#3182bd'],
                label_font_size=14,
                major_guide_stroke_dasharray= '1.5,1.5',
                title_font_size=18,
                major_label_font_size=14,
                legend_font_size=13
            )
        return custom_style


def insert_press_herald_recovered(df):
    recovered_insert = [16,24,36,41,41,68]
    fill_dates = ['2020-03-26','2020-03-27','2020-03-28','2020-03-29','2020-03-30','2020-03-31']
    for idx,rec in enumerate(recovered_insert):
        df.loc[fill_dates[idx]]['recovered'] = rec
    return df


@app.route('/age_range.svg')
@sizes
def plot_age_range(size):
    if size == 'small':
        custom_style = small_style_bar()
        custom_style.title_font_size = 26
        date_rot = 20
    else:
        custom_style = large_style_bar()
        date_rot = 0

    #create a df
    df_age = pd.DataFrame.from_dict({'age_range':['< 20','20s', '30s', '40s',
                                                  '50s', '60s', '70s','80+'],
                                 'cases': [18,85,91,117,169,149,130,116]})
    # add up the total cases and find % of total in each age range
    total_count = df_age.cases.sum()
    df_age['percent_of_tot'] = df_age.cases/total_count*100
    df_age = df_age.round({'percent_of_tot':1})

    # create a bar chart of the age range data
    bar_chart = pygal.Bar(style=custom_style,
                          x_label_rotation=date_rot,
                          show_legend=False,
                          y_title='Percent of Cases (%)',
                          x_title='Age Group')
    bar_chart.title = 'Case Distribution by Patient Age (April 20, 2020)'
    bar_chart.x_labels = df_age.age_range
    bar_chart.add('% of Cases', df_age.percent_of_tot.to_list())

    return bar_chart.render_response()


@app.route('/case_status.svg')
@sizes
def plot_case_status(size):
    if size == 'small':
        custom_style = small_style_bar()
        date_rot = 30
        leg_pos = True
        space_sz = 30
        the_height=900
        the_width=700
    else:
        custom_style = large_style_bar()
        date_rot = 30
        leg_pos = False
        space_sz = 18
        the_height=600
        the_width=850

    # create a df with total cases and deaths in Maine for each day
    df_state_tot = (get_maine_df().pipe(combine_counties))
    # Add the Press Herald Data for recovered cases between 3/26 and 3/31
    df_state_tot = insert_press_herald_recovered(df_state_tot)

    # find the number of active cases
    df_state_tot['active_cases'] = df_state_tot.confirmed - df_state_tot.deaths - df_state_tot.recovered

    # plot the daily total cases, deaths, and recovered
    bar_chart = pygal.StackedBar(style=custom_style,
                                 x_label_rotation=date_rot,
                                 show_minor_x_labels=False,
                                 legend_at_bottom=leg_pos,
                                 spacing=space_sz,
                                 legend_at_bottom_columns=1,
                                 height=the_height,
                                 width=the_width
                                 )
    bar_chart.title = 'Maine COVID-19 Cases by Status'
    bar_chart.x_labels = df_state_tot.index.values.tolist()
    x_skip = len(df_state_tot.index.values)//4
    bar_chart.x_labels_major = df_state_tot.index.values.tolist()[0::x_skip]

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
    else:
        custom_style = large_style_bar()

    # make a df with the total cases, deaths for each day
    df_state_tot = (get_maine_df()
      .pipe(combine_counties))

    # calculate new cases per day
    df_state_tot['new_cases'] = df_state_tot.confirmed.diff()
    df_state_tot['new_cases'][0] = 1

    # plot new cases per day
    bar_chart = pygal.Bar(style=custom_style,
                          x_label_rotation=20,
                          show_minor_x_labels=False,
                          show_legend=False,
                          y_title = 'Number of New Cases')
    bar_chart.title = 'New COVID-19 Cases in Maine per Day'
    bar_chart.x_labels = df_state_tot.index.values.tolist()
    date_skip = len(df_state_tot.index.values)//4
    bar_chart.x_labels_major = df_state_tot.index.values.tolist()[0::date_skip]
    bar_chart.add('Number of New Cases', df_state_tot.new_cases.to_list())

    return bar_chart.render_response()


@app.route('/total_deaths.svg')
@sizes
def plot_deaths(size):
    if size == 'small':
        custom_style = small_style_bar()
        custom_style.title_font_size = 26
    else:
        custom_style = large_style_bar()

    # make a df with the total cases, deaths for each day
    df_state_tot = (get_maine_df()
      .pipe(combine_counties))

    # plot death data
    bar_chart = pygal.Bar(style=custom_style,
                          x_label_rotation=20,
                          show_minor_x_labels=False,
                          show_legend=False,
                          y_title='Total Number of Deaths')
    bar_chart.title = 'Total COVID-19 Deaths in Maine'
    dates = df_state_tot.index.values.tolist()
    bar_chart.x_labels = dates
    date_skip = len(dates)//4
    bar_chart.x_labels_major = dates[0::date_skip]

    bar_chart.add('Total Deaths', df_state_tot.deaths.values.tolist())

    return bar_chart.render_response()


@app.route('/new_deaths.svg')
@sizes
def plot_new_deaths(size):
    if size == 'small':
        custom_style = small_style_bar()
        custom_style.title_font_size = 26
    else:
        custom_style = large_style_bar()

    # make a df with the total cases, deaths for each day
    df_state_tot = (get_maine_df()
      .pipe(combine_counties))

    df_state_tot['new_deaths'] = df_state_tot.deaths.diff()
    df_state_tot['new_deaths'][0] = 0

    bar_chart = pygal.Bar(style=custom_style,
                          x_label_rotation=20,
                          show_minor_x_labels=False,
                          show_legend=False,
                          y_title = 'Number of New Deaths')
    bar_chart.title = 'New COVID-19 Deaths in Maine per Day'
    dates = df_state_tot.index.values.tolist()
    bar_chart.x_labels = dates
    date_skip = len(dates)//4
    bar_chart.x_labels_major = dates[0::date_skip]
    bar_chart.add('Number of New Deaths', df_state_tot.new_deaths.to_list())

    return bar_chart.render_response()


@app.route('/cases_by_county.svg')
@sizes
def plot_current_cases_by_county(size):
    df_current_county = get_most_recent_data()
    df_current_county.sort_values(by=['confirmed'], ascending=False, inplace=True)

    if size == 'small':
        custom_style = small_style_bar()
        date_skip = 4
        date_rot = 30
        leg_pos = True
        space_sz = 34
        the_height = 900
        the_width = 700
        x_rot = 90
        leg_pos = True
    else:
        custom_style = large_style_bar()
        x_rot = 90
        custom_style.legend_font_size = 16
        leg_pos = False
        the_height=600
        the_width=850
        space_sz = 12

    # calculate current cases
    df_current_county['active_cases'] = df_current_county.confirmed - \
                                        df_current_county.deaths - df_current_county.recovered

    # plot the data
    bar_chart = pygal.StackedBar(style=custom_style,
                                 x_label_rotation=x_rot,
                                 y_title='Number of Cases',
                                 legend_at_bottom=leg_pos,
                                 legend_at_bottom_columns=1,
                                 height=the_height,
                                 width=the_width,
                                 spacing=space_sz)
    bar_chart.title = 'COVID-19 Cases by County' + ' (' + \
                  str(df_current_county.date.max()) + ')'
    bar_chart.x_labels = df_current_county.county.to_list()
    bar_chart.add('Active Cases', df_current_county.active_cases.values.tolist())
    bar_chart.add('Deaths', df_current_county.deaths.values.tolist())
    bar_chart.add('Recovered Cases', df_current_county.recovered.values.tolist())

    return bar_chart.render_response()


@app.route('/cases_per_ten_thousand_res.svg')
@sizes
def plot_cases_per_ten_thousand_res(size):
    if size == 'small':
        custom_style = small_style_bar()
        custom_style.title_font_size = 24
        custom_style.label_font_size = 24
        x_rot=90
        the_height=800
        the_width=650
    else:
        custom_style = large_style_bar()
        x_rot=90
        the_height=600
        the_width=700


    # make a df of the population of Maine counties based on US Census Data
    df_population = create_population_df()
    # make a df for the most recent day's data for Maine
    df_maine_today = get_most_recent_data()
    # add the population data to the NY Times Data
    df_maine_today = df_maine_today.merge(df_population, on='county')
    # calculate cases per 100,000 residents
    df_maine_today['cases_per_ten_thousand'] = df_maine_today.confirmed/ \
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
                          x_title='County',
                          truncate_legend=-1,
                          height=the_height,
                          width=the_width
                          )
    title_text = 'COVID-19 Cases per 10,000 Residents' + ' (' + \
                  str(df_maine_today.date.max()) + ')'
    bar_chart.title = title_text
    bar_chart.x_labels = df_maine_today.county.to_list()
    bar_chart.add('Cases per 10,000 Residents', df_maine_today.cases_per_ten_thousand.to_list())

    return bar_chart.render_response()


@app.route('/cases_vs_pop_density.svg')
@sizes
def plot_cases_vs_pop_density(size):
    if size == 'small':
        custom_style = small_style_bar()
        custom_style.title_font_size = 24
        custom_style.colors=['#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5',
                            '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5',
                            '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5']
    else:
        custom_style = large_style_bar()
        custom_style.colors=['#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5',
                            '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5',
                            '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5', '#3F51B5']
        date_skip = 3

    # make a df of the population of Maine counties based on US Census Data
    df_population = create_population_df()
    # make a df for the most recent day's NY Times data for Maine
    df_maine_today = get_most_recent_data()
    # add the population data to the NY Times Data
    df_maine_today = df_maine_today.merge(df_population, on='county')
    # calculate cases per 100,000 residents
    df_maine_today['cases_per_ten_thousand'] = df_maine_today.confirmed/ \
                                                    (df_maine_today.population/10000)
    df_maine_today = df_maine_today.round({'cases_per_ten_thousand':1})
    # Calculate the population density of each county
    df_maine_today['pop_density'] = df_maine_today.population/df_maine_today.county_area_sq_mile
    df_maine_today = df_maine_today.round({'pop_density':0})
    # Drop the Unknown county row
    unknown_idx = df_maine_today[df_maine_today.county=='Unknown'].index
    df_maine_today = df_maine_today.drop(labels=unknown_idx, axis=0)

    # plot the data
    xy_chart = pygal.XY(style=custom_style,
                        show_legend=False,
                        y_title='Cases per 10,000 People',
                        x_title='Population Density (pop./sq. mile)',
                        stroke=False,
                        dots_size=3
                        )
    title_text = 'Case Load vs Population Density by County' + ' (' + \
                  str(df_maine_today.date.max()) + ')'
    xy_chart.title = title_text
    # plot the data for each county
    for index, row in df_maine_today.iterrows():
        pop_data = [(row['pop_density'], row['cases_per_ten_thousand'])]
        xy_chart.add(row.county, pop_data)

    return xy_chart.render_response()


@app.route('/growth_by_county.svg')
@sizes
def plot_growth_by_county(size):
    df_maine = get_maine_df()
    config = line_config(size)
    dates = list(df_maine.date.unique())
    if size == 'small':
        the_height = 800
        the_width = 600
        leg_pos = True
        space_sz = 26
    else:
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
                            x_label_rotation=30,
                            legend_at_bottom_columns=2,
                            show_dots=False)
    line_chart.title = 'COVID-19 Case Growth by County'
    line_chart.x_labels = list(df_maine.date.unique())
    date_skip = len(df_maine.date.unique())//3
    line_chart.x_labels_major = list(df_maine.date.unique())[0::date_skip]
    #add a line for each county
    plot_county_lines(df_maine, line_chart)

    return line_chart.render_response()


@app.route('/growth_by_county_log.svg')
@sizes
def plot_growth_by_county_log(size):
    df_maine = get_maine_df()
    config = line_config(size)
    dates = list(df_maine.date.unique())
    if size == 'small':
        the_height = 1100
        the_width = 600
        leg_pos = True
        space_sz = 26
    else:
        the_height = 500
        the_width = 800
        leg_pos = False
        space_sz = 14

    # Import the data
    df_maine = get_maine_df()
    # Setup Configuration
    config = line_config(size)
    # Plot the data
    line_chart = pygal.Line(config,
                            y_title='Cases',
                            logarithmic=True,
                            x_label_rotation=30,
                            height=the_height,
                            width=the_width,
                            legend_at_bottom=leg_pos,
                            spacing=space_sz,
                            legend_at_bottom_columns=1,
                            show_dots=False,
                            range=(0, int(df_maine.confirmed.max()))
                            )
    line_chart.title = 'COVID-19 Case Growth by County (log scale)'
    line_chart.x_labels = list(df_maine.date.unique())
    date_skip = len(df_maine.date.unique())//3
    line_chart.x_labels_major = list(df_maine.date.unique())[0::date_skip]
    #add a line for each county
    plot_county_lines(df_maine, line_chart)
    # Set the stoke style for the reference lines and plot them
    ref_style = stroke_style={'width':3}
    line_chart.add('Cases Double every 5 Days', create_days_to_double_data(df_maine, 5),
                  stroke_style=ref_style)
    line_chart.add('Cases Double every Week', create_days_to_double_data(df_maine, 7),
                   stroke_style=ref_style)
    line_chart.add('Cases Double every 10 Days', create_days_to_double_data(df_maine, 10),
                   stroke_style=ref_style)

    return line_chart.render_response()


@app.route('/hospitalization.svg')
@sizes
def plot_hospitalization(size):
    custom_style = get_custom_style_assets(size)

    if size == 'small':
        leg_pos = True
        space_sz = 38
        custom_style.legend_font_size = 28
        custom_style.title_font_size = 30
        custom_style.major_label_font_size=26
    else:
        leg_pos=False
        space_sz = 20
        custom_style.legend_font_size = 18

    # make a df with the total cases, deaths for each day
    df_state_tot = (get_maine_df()
      .pipe(combine_counties))

    line_chart = pygal.Line(style=custom_style,
                            include_x_axis=True,
                            x_label_rotation=20,
                            show_minor_x_labels=False,
                            y_labels_major_every=2,
                            show_minor_y_labels=False,
                            truncate_legend=-1,
                            legend_at_bottom=leg_pos,
                            spacing=space_sz,
                            legend_at_bottom_columns=2)
    line_chart.title = 'Total Patients Ever Hospitalized for COVID-19 in Maine'
    dates = df_state_tot.index.values.tolist()
    line_chart.x_labels = dates
    date_skip = len(dates)//4
    line_chart.x_labels_major = df_state_tot.index.values.tolist()[0::date_skip]
    line_chart.add('Total Hospitalized', df_state_tot.hospitalizations.values.tolist(),
                   stroke_style={'dasharray': '3, 6', 'width':2.5})

    return line_chart.render_response()


@app.route('/ventilators.svg')
@sizes
def plot_ventilators(size):
    custom_style = get_custom_style_assets(size)

    if size == 'small':
        space_sz = 34
        custom_style.colors=['#08519c', '#3182bd', '#6baed6']
        the_width=700
        the_height=800
        custom_style.title_font_size = 28
        custom_style.legend_font_size = 22
    else:
        space_sz = 24
        custom_style.legend_font_size= 14
        custom_style.colors=['#08519c', '#3182bd', '#6baed6']
        the_width=550
        the_height=500

    hosp_assets_dict = create_hospital_assets_dict()

    line_chart = pygal.Line(style=custom_style,
                            dots_size=2,
                            x_label_rotation=20,
                            show_minor_x_labels=False,
                            y_labels_major_every=2,
                            show_minor_y_labels=False,
                            truncate_legend=-1,
                            legend_at_bottom=True,
                            spacing=space_sz,
                            legend_at_bottom_columns=1,
                            height=the_height,
                            width=the_width,
                           )

    line_chart.title = 'Statewide Ventilator Availablity'
    dates = hosp_assets_dict['date']
    line_chart.x_labels = dates
    date_skip = len(dates)//3
    line_chart.x_labels_major = hosp_assets_dict['date'][0::date_skip]

    line_chart.add('Total Ventilators (including alternative)', hosp_assets_dict['total_vent_including_alt'],
                   stroke_style={'width':2.5}, show_dots=1, dots_size=1)
    line_chart.add('Total Traditional Ventilators', hosp_assets_dict['total_ventilators'],
                   stroke_style={'width':2.5}, show_dots=1, dots_size=1)
    line_chart.add('Occupied Ventilators', hosp_assets_dict['occupied_ventilators'],
                  stroke_style={'dasharray': '3, 6', 'width':2.5})

    return line_chart.render_response()


@app.route('/icu_beds.svg')
@sizes
def plot_icu_beds(size):
    custom_style = get_custom_style_assets(size)

    if size == 'small':
        space_sz = 34
        the_width=700
        the_height=800
        custom_style.legend_font_size = 26
        custom_style.title_font_size = 28
    else:
        space_sz = 24
        the_width=550
        the_height=500

    hosp_assets_dict = create_hospital_assets_dict()

    line_chart = pygal.Line(style=custom_style,
                            dots_size=2.5,
                            x_label_rotation=20,
                            truncate_legend=-1,
                            show_minor_x_labels=False,
                            y_labels_major_every=2,
                            show_minor_y_labels=False,
                            legend_at_bottom=True,
                            spacing=space_sz,
                            legend_at_bottom_columns=1,
                            height=the_height,
                            width=the_width,
                            )
    line_chart.title = 'Statewide ICU Bed Availablity'
    dates = hosp_assets_dict['date']
    line_chart.x_labels = dates
    date_skip = len(dates)//3
    line_chart.x_labels_major = hosp_assets_dict['date'][0::date_skip]

    line_chart.add('Total ICU Beds', hosp_assets_dict['total_icu_beds'], stroke_style={'width':2.5},
                   show_dots=1, dots_size=1)
    line_chart.add('Occupied ICU Beds', hosp_assets_dict['occupied_icu_beds'],
                   stroke_style={'dasharray': '3, 6', 'width':2.5})

    return line_chart.render_response()
