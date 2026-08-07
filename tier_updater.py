import urllib.request
import urllib.error
import sys
import math
import os
import json
import shutil
import argparse

# ==========================================
# 1. Configuration Settings
# ==========================================
STATS_FILE = "stats.txt"
REPORT_FILE = "tier_shift_report.txt"
TIERS_FILE = "tiers.json"

# Standard Settings
base_t = 8
x_value = 0.5
end_of_gen_mode = True

# Put any recently banned Pokemon here so the script ignores their high usage
recently_banned = ["Vulpix", "Gastly"]

# ==========================================
# 2. Download & Processing Logic
# ==========================================
def load_tiers_file(filepath):
    """Loads the tier data from the JSON file."""
    if not os.path.exists(filepath):
        print(f" Error: Could not find '{filepath}'. Please create the file first!")
        sys.exit(1)
        
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f" Error: '{filepath}' contains invalid JSON data.")
            sys.exit(1)

def update_and_save_tiers(filepath, backup_filename, tier_data, rises, drops):
    """Updates the dictionary with shifts and saves it back to the JSON file."""
    # Preserve the current tier data before overwriting it with new shifts.
    backup_path = os.path.join(os.path.dirname(filepath), backup_filename)
    shutil.copy2(filepath, backup_path)
    print(f" Created backup of current tiers at '{backup_path}'.")

    # Process Rises (Move to LC OU)
    for mon in rises:
        for t in tier_data:
            # Remove mon from its current tier (case-insensitive check)
            tier_data[t] = [m for m in tier_data[t] if m.lower() != mon.lower()]
        tier_data["LC OU"].append(mon)
        
    # Process Drops (Move to LC UU)
    for mon in drops:
        for t in tier_data:
            tier_data[t] = [m for m in tier_data[t] if m.lower() != mon.lower()]
        tier_data["LC UU"].append(mon)
        
    # Format and sort arrays alphabetically for cleanliness
    for t in tier_data:
        # Standardize capitalization
        tier_data[t] = ['-'.join(word.capitalize() for word in m.split('-')) for m in tier_data[t]]
        tier_data[t] = sorted(tier_data[t])
        
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(tier_data, f, indent=4)
    print(f" Updated tiers successfully saved to '{filepath}'!")

def download_stats(stats_url, allow_existing_stats=True):
    print(f"\nAttempting to download stats from:\n{stats_url}\n")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
        req = urllib.request.Request(stats_url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
            
            if "<!doctype html>" in content[:100].lower() or "<html" in content[:100].lower():
                print(" ERROR: Blocked by Cloudflare!")
                print("The server sent a security webpage instead of the stats file.")
                if allow_existing_stats and os.path.exists(STATS_FILE):
                    print(" Proceeding with existing local file...")
                    return True
                return False

            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                f.write(content)
                
        print(f" Success! True text downloaded and saved as '{STATS_FILE}'.")
        return True

    except urllib.error.HTTPError as e:
        print(f" HTTP Error {e.code}: The server rejected the request or the file doesn't exist.")
    except Exception as e:
        print(f" Download failed: {e}")

    if allow_existing_stats and os.path.exists(STATS_FILE):
        print(" Proceeding with existing local file...")
        return True

    print(" No usable local stats file is available.")
    return False

def read_local_stats(filepath):
    usage_dict = {}
    print(f"\nReading local file: {filepath}...")
    
    if not os.path.exists(filepath):
        print(f" Error: Could not find '{filepath}'.")
        print("Please save the Smogon text data into 'stats.txt' in this folder first!")
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            clean_line = line.strip()
            if clean_line.startswith('|') and 'Rank' not in clean_line:
                parts = clean_line.split('|')
                if len(parts) > 3:
                    pokemon = parts[2].strip()
                    usage_str = parts[3].strip().replace('%', '')
                    try:
                        usage_dict[pokemon] = float(usage_str) / 100.0
                    except ValueError:
                        continue
                        
    if not usage_dict:
        print(" Error: File read successfully, but no Pokémon data found.")
        print("Double check that you actually pasted the Smogon stats into stats.txt!")
        
    return usage_dict

def calculate_cutoff(t, x):
    effective_x = min(x, 1.0)
    return 1 - math.pow((1 - effective_x), 1 / t)

def evaluate_tier_shifts(prev_tiers, usage_data, current_cutoff, rises_allowed, banned_list):
    rises = []
    drops = []
    
    for mon, current_tier in prev_tiers.items():
        if current_tier in ["LC Ubers", "LC UU BL", "LC RU BL"] or mon in banned_list:
            continue
            
        usage = usage_data.get(mon, 0.0)
        
        if current_tier == "LC OU" and usage < current_cutoff:
            drops.append(mon)
            
        elif current_tier in ["LC UU", "LC RU", "The rest"] and usage >= current_cutoff:
            if rises_allowed:
                rises.append(mon)
                
    for mon, usage in usage_data.items():
        if mon not in prev_tiers and usage >= current_cutoff and mon not in banned_list:
            if rises_allowed:
                rises.append(mon)
            
    return rises, drops

# ==========================================
# 3. Interactive Menu & Execution
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*40)
    print("      LC TIER UPDATER - CONFIGURATION")
    print("="*40)

    parser = argparse.ArgumentParser(description="Update LC tiers from monthly Smogon usage stats.")
    parser.add_argument("--date", dest="stats_date", help="Stats month in YYYY-MM format, for example 2026-07.")
    parser.add_argument(
        "--strict-download",
        action="store_true",
        help="Fail instead of using an existing stats.txt file when the download fails."
    )
    args = parser.parse_args()
    
    # Get Year and Month
    while True:
        if args.stats_date:
            yyyy_mm = args.stats_date.strip()
        else:
            yyyy_mm = input("Enter the stats Year and Month (e.g., 2026-06) [Default: 2026-06]: ").strip() or "2026-06"
        if len(yyyy_mm) == 7 and '-' in yyyy_mm:
            try:
                month_int = int(yyyy_mm.split('-')[1])
                if 1 <= month_int <= 12:
                    break
            except ValueError:
                pass
        print(" Please enter a valid date in YYYY-MM format (e.g., 2026-06).")
        if args.stats_date:
            sys.exit(1)
        
    dynamic_stats_url = f"https://www.smogon.com/stats/{yyyy_mm}/gen9lc-1630.txt"
    backup_filename = f"tiers_backup_{yyyy_mm.replace('-', '')}.json"

    # Automatically determine the Quarter and Cycle Month
    if month_int in [12, 1, 2]:
        cycle_quarter = "Q1"
        cycle_month = {12: 1, 1: 2, 2: 3}[month_int]
    elif month_int in [3, 4, 5]:
        cycle_quarter = "Q2"
        cycle_month = {3: 1, 4: 2, 5: 3}[month_int]
    elif month_int in [6, 7, 8]:
        cycle_quarter = "Q3"
        cycle_month = {6: 1, 7: 2, 8: 3}[month_int]
    elif month_int in [9, 10, 11]:
        cycle_quarter = "Q4"
        cycle_month = {9: 1, 10: 2, 11: 3}[month_int]

    # Tier shifts are published for the month after the usage-stat month.
    display_month = ["January", "February", "March", "April", "May", "June",
                     "July", "August", "September", "October", "November", "December"][month_int % 12]

    # Load live tiers from the JSON file
    raw_tier_data = load_tiers_file(TIERS_FILE)
    
    # Flatten the dictionary and format capitalizations for evaluation
    formatted_banned = ['-'.join(word.capitalize() for word in mon.split('-')) for mon in recently_banned]
    previous_tiers = {}
    for tier, mons in raw_tier_data.items():
        for mon in mons:
            formatted_mon = '-'.join(word.capitalize() for word in mon.split('-'))
            previous_tiers[formatted_mon] = tier

    # Dynamic Math
    if cycle_month == 1:
        t_value = base_t
        t_expression = "base_t"
        allow_rises = True
    elif cycle_month == 2:
        t_value = base_t * 2
        t_expression = "base_t * 2"
        allow_rises = False
    elif cycle_month == 3:
        t_value = base_t * 3
        t_expression = "base_t * 3"
        allow_rises = False

    if end_of_gen_mode:
        allow_rises = False

    print(f"\n Recognized Date: {cycle_quarter} - Month {cycle_month}")
    print(" Configuration Saved! Initiating Download...")

    # Download and process stats
    if not download_stats(dynamic_stats_url, allow_existing_stats=not args.strict_download):
        sys.exit(1)
    current_usage = read_local_stats(STATS_FILE)

    if current_usage:
        cutoff = calculate_cutoff(t_value, x_value)
        rises, drops = evaluate_tier_shifts(previous_tiers, current_usage, cutoff, allow_rises, formatted_banned)
        
        # Build the report string
        report_lines = []
        report_lines.append("========== TIER SHIFT REPORT ==========")
        report_lines.append("")
        report_lines.append('[SPOILER="Base Data"]')
        report_lines.append("")
        report_lines.append(f"Cycle: {cycle_quarter} - Month {cycle_month} ({display_month})")
        report_lines.append("")
        
        if not allow_rises:
            report_lines.append("Mode: Quick Drops Only (Rises Locked)")
        elif end_of_gen_mode:
            report_lines.append("Mode: End of Generation (Rises Locked)")
        else:
            report_lines.append("Mode: Full Standard Shifts")

        report_lines.append("")
        report_lines.append(f"Teams Parameter (T): {t_value} ({t_expression})")
        report_lines.append("")
        report_lines.append(f"Applied Cutoff: {cutoff * 100:.2f}%")
        report_lines.append("")
        report_lines.append("[/SPOILER]")
        report_lines.append("")

        report_lines.append("**Rises (To LC OU):**")
        if not allow_rises:
            report_lines.append("None (Rises are locked for this cycle phase)")
        elif rises:
            for mon in sorted(rises):
                usage_pct = current_usage.get(mon, 0) * 100
                report_lines.append(f":{mon.lower().replace(' ', '-')}: {mon} ({usage_pct:.2f}%)")
        else:
            report_lines.append("None")

        report_lines.append("")
        report_lines.append("**Drops (From LC OU):**")
        if drops:
            for mon in sorted(drops):
                usage_pct = current_usage.get(mon, 0) * 100
                report_lines.append(f":{mon.lower().replace(' ', '-')}: {mon} ({usage_pct:.2f}%)")
        else:
            report_lines.append("None")
        report_lines.append("=======================================")
        
        final_report = "\n".join(report_lines)
        print(f"\n{final_report}")
        
        # Save output to text file
        try:
            with open(REPORT_FILE, "w", encoding="utf-8") as file:
                file.write(final_report)
            print(f"\n Report successfully saved to '{REPORT_FILE}'!")
        except IOError as e:
            print(f"\n Could not save to file: {e}")

        # Update and save the tiers JSON file if there were any shifts
        if rises or drops:
            update_and_save_tiers(TIERS_FILE, backup_filename, raw_tier_data, rises, drops)
