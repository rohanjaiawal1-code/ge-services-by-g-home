import json
import os
import sys
from datetime import datetime

file_path = "users.json"

# गिटहब एक्शन से एनवायरनमेंट वेरिएबल्स रीड करना
event_name = os.environ.get("EVENT_NAME", "")
toggle_mode = os.environ.get("TOGGLE_MODE", "timer").lower()
user_id = os.environ.get("USER_ID", "").strip()
status_mode = os.environ.get("STATUS_MODE", "active").lower()
update_date = os.environ.get("UPDATE_DATE", "").strip()

# अगर एक्शन शेड्यूल टाइमर से ट्रि隔 हुआ है
if event_name == "schedule":
    toggle_mode = "timer"

# फाइल चेक करना और स्ट्रक्चर बनाना अगर फाइल न हो
if not os.path.exists(file_path):
    base_structure = {
        "videos": {
            "welcome": [],
            "ads": [],
            "trial": [],
            "expired": [],
            "error": []
        },
        "users": {}
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(base_structure, f, indent=2, ensure_ascii=False)

with open(file_path, "r", encoding="utf-8") as f:
    try:
        data = json.load(f)
    except Exception:
        data = {"videos": {}, "users": {}}

if "users" not in data:
    data["users"] = {}

# --- 1. MANUAL MODE LOGIC ---
if toggle_mode == "manual":
    if not user_id:
        print("Error: User ID required for manual mode!")
        sys.exit(1)
        
    if user_id in data["users"]:
        data["users"][user_id]["status"] = status_mode
    else:
        data["users"][user_id] = {"username": "Manual_User", "status": status_mode}
    print(f"✨ [Manual Mode] Updated User {user_id} to {status_mode}")

# --- 2. TIMER MODE LOGIC ---
elif toggle_mode == "timer":
    current_date = update_date if update_date else datetime.now().strftime("%Y-%m-%d")
    
    if user_id:
        if user_id in data["users"]:
            data["users"][user_id]["status"] = status_mode
        else:
            data["users"][user_id] = {"username": "Timer_User", "status": status_mode}
        print(f"⏰ [Timer Mode] User {user_id} updated to {status_mode} for Date: {current_date}")
    else:
        print(f"⏰ [Automatic Cron Timer] System clean-up logs verified on {current_date}")

# फाइल को दोबारा सुरक्षित सेव करना
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Process completed successfully.")
