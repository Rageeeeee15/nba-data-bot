import requests
import pandas as pd
import random
from bs4 import BeautifulSoup

# --- 1. THE MAP ---
impact_map = {
    "Giannis Antetokounmpo": [("Damian Lillard", 6.5), ("Myles Turner", 5.0)],
    "Shai Gilgeous-Alexander": [("Jalen Williams", 6.0), ("Chet Holmgren", 4.5)],
    "Luka Doncic": [("Kyrie Irving", 5.0), ("Klay Thompson", 4.5)],
    "Jimmy Butler": [("Tyler Herro", 4.5), ("Bam Adebayo", 4.0)],
    "Joel Embiid": [("Tyrese Maxey", 6.5)]
}

def get_nba_data():
    active_boosts = {}
    # We will use this list to REMOVE players from the final sheet
    injury_list = [] 
    
    # --- REAL TIME INJURY SCRAPE ---
    try:
        url = "https://www.cbssports.com/nba/injuries/"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        page_text = soup.get_text()

        for star in impact_map.keys():
            if star in page_text:
                print(f"🚑 CONFIRMED OUT: {star}")
                injury_list.append(star) # Add to "Do Not Show" list
                for teammate, boost in impact_map[star]:
                    active_boosts[teammate] = active_boosts.get(teammate, 0) + boost
    except:
        print("⚠️ Injury site down, using manual star list.")

    # --- ODDS DATA ---
    lines = [
        {'name': "Damian Lillard", 'line': 28.5},
        {'name': "Myles Turner", 'line': 17.5},
        {'name': "Jalen Williams", 'line': 23.5},
        {'name': "Kyrie Irving", 'line': 26.5},
        {'name': "Tyler Herro", 'line': 21.5},
        {'name': "Jimmy Butler", 'line': 22.5} # Added to test the filter
    ]
    return lines, active_boosts, injury_list

def run_analysis():
    lines, boosts, bans = get_nba_data()
    results = []
    
    for p in lines:
        name = p['name']
        
        # --- THE HARD FILTER ---
        # If the player is injured, SKIP them. Do not even put them in the table.
        if name in bans:
            continue 
            
        line = p['line']
        boost = boosts.get(name, 0)
        ai_proj = line + boost
        edge_pct = (boost / line * 100) if line > 0 else 0
        
        grade = "❌ PASS"
        if edge_pct > 10: grade = "🔥 ELITE"
        elif edge_pct > 5: grade = "✅ VALUE"
        
        results.append({
            "Player": name,
            "Line": line,
            "Boost": boost,
            "AI_Proj": ai_proj,
            "Grade": grade
        })
    return pd.DataFrame(results)

if __name__ == "__main__":
    df = run_analysis()
    df.to_csv("nba_all_stats.csv", index=False)
    # This only shows you the players who are actually playing
    print("\n🏀 --- ACTIVE PLAYER PREDICTIONS --- 🏀")
    print(df.to_string(index=False))
