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

# अगर एक्शन शेड्यूल टाइमर (Cron) से ट्रिगर हुआ है
if event_name == "schedule":
    toggle_mode = "timer"

# फाइल चेक करना
if not os.path.exists(file_path):
    print(f"Error: {file_path} not found!")
    sys.exit(1)

with open(file_path, "r", encoding="utf-8") as f:
    try:
        data = json.load(f)
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        sys.exit(1)

if "users" not in data:
    data["users"] = {}

# करंट लाइव टाइमस्टैम्प बनाना (Format: YYYY-MM-DDTHH:MM:SS.mmmZ)
current_utc = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

# तय करना कि कौन सी तारीख सेव करनी है
if toggle_mode == "timer" and update_date:
    # अगर आपने टाइमर में खास तारीख (जैसे 2026-07-12) दी है
    timestamp_to_save = f"{update_date}T00:00:00.000Z"
else:
    timestamp_to_save = current_utc

# वैलिडेशन
if not user_id and toggle_mode == "manual":
    print("Error: User ID required for manual mode!")
    sys.exit(1)

# यूजर डेटा प्रोसेस करना
if user_id:
    if user_id in data["users"]:
        # पुराने यूजर का पुराना यूजरनेम बिना छेड़े सिर्फ स्टेटस और तारीख अपडेट करना
        data["users"][user_id]["status"] = status_mode
        data["users"][user_id]["updated_at"] = timestamp_to_save
        print(f"✨ [Existing User] {user_id} updated to {status_mode} with date {timestamp_to_save}")
    else:
        # अगर नया यूजर है तो नया रिकॉर्ड बनाना
        data["users"][user_id] = {
            "username": "GE_User",
            "status": status_mode,
            "updated_at": timestamp_to_save
        }
        print(f"✨ [New User Created] {user_id} saved with status {status_mode}")
else:
    print(f"⏰ [Automatic Cron Timer] System verification logs checked at {current_utc}")

# फाइल को दोबारा सुंदर फॉर्मेट में सेव करना
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Process completed successfully.")
