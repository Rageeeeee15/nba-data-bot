import pandas as pd
from nba_api.stats.endpoints import leaguegamelog

def update_data():
    # Fetch the entire league's data for the current season
    log = leaguegamelog.LeagueGameLog(player_or_team_abbreviation='P')
    df = log.get_data_frames()[0]
    # Save it as a CSV
    df.to_csv('nba_all_stats.csv', index=False)
    print("NBA Data Updated Successfully!")

if __name__ == "__main__":
    update_data()
