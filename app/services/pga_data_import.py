import pandas as pd
import numpy as np

def calculate_weighted_sg(df, player_name, window_size=5, weights=[0.4, 0.3, 0.2, 0.1]):
  
  """
  This function calculates the weighted average of strokes gained metrics for a player
  based on the last 'window_size' tournaments (excluding the current one).

  Args:
      df: The pandas DataFrame containing the golf tournament data.
      player_name: The name of the player for whom to calculate the weighted average.
      window_size: The number of previous tournaments to consider (default: 5).
      weights: A list of weights for each previous tournament (default: [0.4, 0.3, 0.2, 0.1]).

  Returns:
      A dictionary containing the weighted average for each sg metric (sg_putt, sg_arg, etc.).
  """

  # Filter data for the specific player
  player_data = df[df['player_name'] == player_name]

  # Sort data by date in descending order (newest to oldest)
  player_data = player_data.sort_values(by='date', ascending=False)

  # Initialize empty dictionary to store weighted averages
  weighted_sg = {}
  for metric in ['sg_putt', 'sg_arg', 'sg_app', 'sg_ott', 'sg_t2g', 'sg_total']:
    weighted_sg[metric] = 0

  # Loop through available previous tournaments (up to window_size)
  for i in range(1, min(window_size, len(player_data))):
    # Get the current and previous tournament data
    current_data = player_data.iloc[0]
    previous_data = player_data.iloc[i]

    # Calculate the weighted average for each metric
    for metric in weighted_sg.keys():
      weighted_sg[metric] += previous_data[metric] * weights[i - 1]

  # Normalize the weighted average by the number of available data points
  if len(player_data) > 1:
    # Avoid division by zero if only one data point available
    norm_factor = sum(weights)
  else:
    norm_factor = len(player_data)
  for metric in weighted_sg.keys():
    weighted_sg[metric] /= norm_factor

  # Round the weighted averages to 3 decimal places
  for metric in weighted_sg.keys():
    weighted_sg[metric] = round(weighted_sg[metric], 3)

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

    # Loop through each player name in the dataframe
    for player_name in df['player_name'].unique():
        
        # Calculate weighted sg for the player and store it in the dictionary
        weighted_sg_data[player_name] = calculate_weighted_sg(df.copy(), player_name)  # Pass a copy to avoid modifying original df
        
    # Add new columns to the dataframe for each weighted sg metric
    for metric, _ in weighted_sg_data[list(weighted_sg_data.keys())[0]].items():
        df[f'weighted_{metric}'] = df['player_name'].apply(lambda x: weighted_sg_data[x][metric])

    data_for_sql = df.to_dict('records')
    
    print("CSV historical data looks good!")

    return data_for_sql