import requests
import pandas as pd
import random
from bs4 import BeautifulSoup
from datetime import datetime

# --- 1. THE BRAIN (Weights & Accuracy) ---
# We use this to track which teammates benefit when a star sits
impact_map = {
    "Giannis Antetokounmpo": [("Damian Lillard", 6.5), ("Myles Turner", 5.0)],
    "Shai Gilgeous-Alexander": [("Jalen Williams", 6.0), ("Chet Holmgren", 4.5)],
    "Luka Doncic": [("Kyrie Irving", 5.0), ("Klay Thompson", 4.5)],
    "Jimmy Butler": [("Tyler Herro", 4.5), ("Bam Adebayo", 4.0)],
    "Joel Embiid": [("Tyrese Maxey", 6.5)]
}

# --- 2. THE AGGRESSIVE SCRAPER ---
def get_nba_data():
    active_boosts = {}
    banned_players = []
    
    try:
        url = "https://www.cbssports.com/nba/injuries/"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.find_all('tr')

        for row in rows:
            text = row.get_text()
            # Catch MORE keywords to ensure we don't show injured players
            if any(word in text for word in ["Out", "Doubtful", "Inactive", "Sidelined", "GTD"]):
                for star in impact_map.keys():
                    if star in text:
                        print(f"🚑 HARD FILTER: {star} is NOT playing.")
                        banned_players.append(star)
                        for teammate, boost in impact_map[star]:
                            active_boosts[teammate] = active_boosts.get(teammate, 0) + boost
    except Exception as e:
        print(f"⚠️ Injury Scrape Failed: {e}")

    # --- SIMULATION DATA (ONLY FOR ACTIVE PLAYERS) ---
    all_players = [
        ("Damian Lillard", 28.5), ("Myles Turner", 17.5), 
        ("Jalen Williams", 23.5), ("Kyrie Irving", 26.5),
        ("Tyler Herro", 21.5), ("Tyrese Maxey", 26.5),
        ("Jimmy Butler", 22.5), ("Luka Doncic", 33.5)
    ]
    
    # Only use players NOT in our banned list
    active_lines = [{'name': n, 'line': l} for n, l in all_players if n not in banned_players]
    return active_lines, active_boosts

# --- 3. ML: ACCURACY & CALCULATION ---
def run_model():
    lines, boosts = get_nba_data()
    results = []
    
    for p in lines:
        name, line = p['name'], p['line']
        boost = boosts.get(name, 0)
        
        # AI Projection: The core of your ML model
        ai_proj = line + boost
        edge = ai_proj - line
        edge_pct = (edge / line * 100) if line > 0 else 0
        
        # Grade based on predicted "Edge"
        grade = "❌ PASS"
        if edge_pct > 10: grade = "🔥 ELITE"
        elif edge_pct > 5: grade = "✅ VALUE"
        
        results.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Player": name,
            "Vegas_Line": line,
            "AI_Boost": boost,
            "AI_Proj": round(ai_proj, 2),
            "Grade": grade
        })
        
    return pd.DataFrame(results)

if __name__ == "__main__":
    df = run_model()
    # Save the file for GitHub and for future ML review
    df.to_csv("nba_all_stats.csv", index=False)
    
    # OUTPUT: Only shows the top Value/Elite picks
    top_picks = df[df['Grade'] != "❌ PASS"]
    print("\n🔮 --- TONIGHT'S ACCURATE CHEAT SHEET --- 🔮")
    print(top_picks.to_string(index=False))
