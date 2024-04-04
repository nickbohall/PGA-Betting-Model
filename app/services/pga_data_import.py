import pandas as pd
import numpy as np

def calculate_weighted_sg(df, player_name, window_size=4, weights=[0.4, 0.3, 0.2, 0.1]):
    """
    This function calculates the weighted average of strokes gained metrics for a player
    based on the last 'window_size' tournaments (excluding the current one).

    Args:
        df: The pandas DataFrame containing the golf tournament data.
        player_name: The name of the player for whom to calculate the weighted average.
        window_size: The number of previous tournaments to consider (default: 4).
        weights: A list of weights for each previous tournament (default: [0.4, 0.3, 0.2, 0.1]).

    Returns:
        A dictionary containing the weighted average for each sg metric (sg_putt, sg_arg, etc.).
    """

    # Filter data for the specific player
    player_data = df[df['player_name'] == player_name]

    # Sort data by date in ascending order (oldest to newest)
    player_data = player_data.sort_values(by='date', ascending=True)

    # Limit the data to the last 'window_size' tournaments
    player_data = player_data.iloc[-window_size:]

    # Initialize empty dictionary to store weighted averages
    weighted_sg = {}
    for metric in ['sg_putt', 'sg_arg', 'sg_app', 'sg_ott', 'sg_t2g', 'sg_total']:
        weighted_sg[metric] = 0

    # Check if there are previous tournaments for the player
    if len(player_data) > 0:
        # Loop through available previous tournaments
        for i, (_, tournament) in enumerate(player_data.iterrows()):
            # Calculate the weighted average for each metric
            for metric in weighted_sg.keys():
                weighted_sg[metric] += tournament[metric] * weights[i]

        # Normalize the weighted average by the sum of weights
        norm_factor = sum(weights[:len(player_data)])
        for metric in weighted_sg.keys():
            weighted_sg[metric] /= norm_factor

        # Round the weighted averages to 3 decimal places
        for metric in weighted_sg.keys():
            weighted_sg[metric] = round(weighted_sg[metric], 3)
    else:
        # Handle case where there are no previous tournaments for the player
        # Set all weighted sg statistics to zero
        for metric in weighted_sg.keys():
            weighted_sg[metric] = -2

    return weighted_sg


def get_historical_data():
    # Reading in historical csv
    path = "C:/Users/Sleepycornbread/Python Projects/Portfolio Projects/PGA Webscraper/Data In/sql_ingest_2015-2022.csv"
    raw_df = pd.read_csv(path)
    raw_df = raw_df.dropna()

    # Changing some datatypes for later
    df = raw_df
    df["year"] = df.year.astype(int)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    # Preprocess the data
    df['finish'] = pd.to_numeric(df['finish'], errors='coerce')
    df['finish'].fillna(99, inplace=True)

    df['score'] = pd.to_numeric(df['score'], errors='coerce')
    df['score'].fillna(99, inplace=True)

    # Strip whitespaces from 'tournament_name' column
    df['tournament_name'] = df['tournament_name'].str.strip()

    # Create an empty dictionary to store weighted sg averages for all players
    weighted_sg_data = {}

    # Iterate through each row in the dataframe
    for i, row in df.iterrows():
        # Get the player name and date of the current tournament
        player_name = row['player_name']
        current_date = row['date']

        # Filter the dataframe to include only previous tournaments for this player
        previous_tournaments = df[(df['player_name'] == player_name) & (df['date'] < current_date)]

        # Calculate the weighted sg for this player based on previous tournaments
        weighted_sg_data[player_name] = calculate_weighted_sg(previous_tournaments, player_name)

        # Update the dataframe with the calculated weighted sg for this tournament
        for metric, value in weighted_sg_data[player_name].items():
            df.at[i, f'weighted_{metric}'] = value

    # Convert dataframe to dictionary for SQL insertion
    data_for_sql = df.to_dict('records')
    
    print("CSV historical data looks good!")

    return data_for_sql

# dict = get_historical_data()
# df = pd.DataFrame(dict)
# print(df.loc[df.player_name == "Scottie Scheffler"])

# dict = get_historical_data()
# df = pd.DataFrame(dict)
# print(df.loc[df.player_name == "Scottie Scheffler"])