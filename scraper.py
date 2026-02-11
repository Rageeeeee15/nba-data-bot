import pandas as pd
from nba_api.stats.endpoints import leaguegamelog
import time

def update_data():
    # These 'Headers' make the NBA website think we are a real person
    custom_headers = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.nba.com/',
        'Origin': 'https://www.nba.com',
    }

    try:
        print("🏀 Fetching NBA data...")
        # We add a 30-second timeout in case the NBA site is slow
        log = leaguegamelog.LeagueGameLog(player_or_team_abbreviation='P', timeout=30)
        df = log.get_data_frames()[0]
        
        # Save it
        df.to_csv('nba_all_stats.csv', index=False)
        print(f"✅ Success! Captured {len(df)} game rows.")
        
    except Exception as e:
        print(f"❌ Error during fetch: {e}")
        exit(1) # This tells GitHub the script failed

if __name__ == "__main__":
    update_data()
