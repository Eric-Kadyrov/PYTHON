import pandas as pd

# Part 2a: Import the dataset and assign it to df variable
url = 'https://raw.githubusercontent.com/guipsamora/pandas_exercises/master/02_Filtering_%26_Sorting/Euro12/Euro_2012_stats_TEAM.csv'  # URL data
df = pd.read_csv(url)

# Part 2b: Select only the Team, Yellow Cards, and Red Cards columns
selected_columns = df[['Team', 'Yellow Cards', 'Red Cards']]

# Part 2c: Count how many teams participated in the Euro2012
num_teams = df['Team'].nunique()
print("Number of teams participated:", num_teams)

# Part 2d: Filter teams that scored more than 6 goals
teams_more_than_6_goals = df[df['Goals'] > 6]  # 'Goals' should be the name of the column that contains the goals information
print("Teams that scored more than 6 goals:\n", teams_more_than_6_goals)