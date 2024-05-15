# PGA Betting Model

The point of this was to create a model that predicts pga player finishes in tournaments and majors.
Data was scraped from the pga website with Selenium & adjustments were made with Python. The data was then extracted and placed into model & schema format to be ingested with APIs into a Postgres database.

The main inputs are below:
1. Players SG (strokes gained) stats
2. Historical tournament finishes
3. Historical Course finishes
4. A "recent form" statistic

The feature engineering and data analysis was done in jupyter notebooks since that was a better place to work with the data.
Other features were brought in and the data was run through a linear and logisitc regression

# Results
Results are TBD. I am still scraping weekly data and will likely need around a year's worth of data before meaningful results are ready.
