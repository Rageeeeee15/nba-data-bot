import requests
import pandas as pd
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime

# --- 1. THE BRAIN (Load Memory) ---
# We use a JSON file to store the "Learned Weights" so they survive restart
BRAIN_FILE = "ai_memory.json"

def load_brain():
    if os.path.exists(BRAIN_FILE):
        with open(BRAIN_FILE, 'r') as f:
            return json.load(f)
    # Default weights if no memory exists
    return {
        "Kyrie Irving": 5.0, "Klay Thompson": 4.5, "P.J. Washington": 3.5,
        "Damian Lillard": 6.5, "Myles Turner": 5.0, "Bobby Portis": 4.5,
        "Jalen Williams": 6.0, "Chet Holmgren": 4.5,
        "Tyrese Maxey": 6.5, "Kelly Oubre Jr": 4.0,
        "Tyler Herro": 4.5, "Bam Adebayo": 4.0
    }

learning_weights = load_brain()

# Relationship Map (Who relies on who?)
impact_map = {
    "Luka Doncic": ["Kyrie Irving", "Klay Thompson", "P.J. Washington"],
    "Giannis Antetokounmpo": ["Damian Lillard", "Myles Turner", "Bobby Portis"],
    "Shai Gilgeous-Alexander": ["Jalen Williams", "Chet Holmgren"],
    "Joel Embiid": ["Tyrese Maxey", "Kelly Oubre Jr"],
    "Jimmy Butler": ["Tyler Herro", "Bam Adebayo"],
}

# --- 2. THE INTELLIGENT SCRAPER ---
def get_nba_data():
    active_boosts = {}
    banned_players = []
    
    # LIST OF EVERYONE WE CARE ABOUT (Stars + Teammates)
    # We must check ALL of them for injuries, not just the stars.
    all_targets = list(impact_map.keys())
    for teammates in impact_map.values():
        all_targets.extend(teammates)

    print("🚑 Scanning Injury Report...")
    try:
        url = "https://www.cbssports.com/nba/injuries/"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text() # Get all text on page
        
        # Check EVERY player in our universe
        for player in all_targets:
            # We check Last Name to catch "K. Irving" or "Irving"
            last_name = player.split()[-1]
            if last_name in text and ("Out" in text or "Doubtful" in text):
                print(f"   ⚠️ INJURY DETECTED: {player}")
                banned_players.append(player)
                
                # If a STAR is out, boost the teammates
                if player in impact_map:
                    for teammate in impact_map[player]:
                        # Use the LEARNED weight, not a hardcoded one
                        boost_amt = learning_weights.get(teammate, 4.0)
                        active_boosts[teammate] = active_boosts.get(teammate, 0) + boost_amt
                        
    except Exception as e:
        print(f"⚠️ Scrape Error: {e}")

    # --- ODDS / SIMULATION ---
    lines = []
    # Our betting pool (Active players only)
    sim_pool = [
        ("Damian Lillard", 28.5), ("Myles Turner", 17.5), 
        ("Jalen Williams", 23.5), ("Kyrie Irving", 26.5),
        ("Tyler Herro", 21.5), ("Tyrese Maxey", 26.5),
        ("Jimmy Butler", 22.5), ("Luka Doncic", 32.5)
    ]
    
    for name, line in sim_pool:
        # STRICT FILTER: If they are banned, they DO NOT pass.
        if name not in banned_players:
            lines.append({'name': name, 'line': line})

    return lines, active_boosts

# --- 3. THE ANALYST ---
def run_model():
    lines, boosts = get_nba_data()
    results = []
    
    for p in lines:
        name = p['name']
        line = p['line']
        boost = boosts.get(name, 0)
        
        ai_proj = line + boost
        edge_pct = ((ai_proj - line) / line * 100) if line > 0 else 0
        
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

# --- 4. THE TEACHER (Self-Correction) ---
def self_correct(df):
    # This simulates checking yesterday's scores (Mock Data for now)
    # In V2, we will scrape actual box scores here.
    actual_scores = {"Damian Lillard": 35, "Tyler Herro": 15} 
    
    updates = False
    for _, row in df.iterrows():
        name = row['Player']
        proj = row['AI_Proj']
        
        if name in actual_scores:
            actual = actual_scores[name]
            diff = actual - proj
            
            # If we missed by a lot, adjust the brain
            if abs(diff) > 5:
                print(f"   🧠 Learning: Adjusted weight for {name}")
                current_weight = learning_weights.get(name, 5.0)
                # If we were too low, increase weight. Too high, decrease.
                learning_weights[name] = current_weight + (0.5 if diff > 0 else -0.5)
                updates = True

    if updates:
        # SAVE THE NEW BRAIN
        with open(BRAIN_FILE, 'w') as f:
            json.dump(learning_weights, f)
        print("💾 Brain updated and saved.")

if __name__ == "__main__":
    df = run_model()
    
    # Run the learning process
    self_correct(df)
    
    df.to_csv("nba_all_stats.csv", index=False)
    print(df.to_string(index=False))
