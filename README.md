## Introduction
This repository is a work in progress, and contains code for a website with visualizations of COVID-19 data in Maine. The visualizations of Maine COVID-19 data that are publicly available are very limited, so we (Berkeley and Andy Almand-Hunter) are working on a website to surface more visualizations to the public. We are not a part of any public health agency, and are just doing this for fun!

## Files
- covid_plots.py is the python code that creates the visualizations
- maine_covid_data.ipynb is not part of the production code, and is used a scratch pad

## Data Sources
Data is sourced from the [Maine CDC](https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml) when possible. The Maine CDC publicizes current snapshots of state and county-level case, death, hospitalization, and recovery data in tables on their website. They do not provide historical data. We began scraping their website on March 31, 2020, and data from then on will be from the Maine CDC.

The NY Times surfaced county-level case, death, and recovery data in GitHub (https://github.com/nytimes/covid-19-data), and that data is used where data is not directly available from the Maine CDC. See the NY Times US Visualizations (https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html) for lots of visualizations on a national level.
