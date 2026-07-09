import json
import os
import sys
from datetime import datetime

file_path = "users.json"

# गिटहब एक्शन से मैन्युअल इनपुट रीड करना
user_id = os.environ.get("USER_ID", "").strip()
status_mode = os.environ.get("STATUS_MODE", "active").lower()

# वैलिडेशन चेक
if not user_id:
    print("Error: User ID (Phone Number) is required!")
    sys.exit(1)

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

# करंट लाइव टाइमस्टैम्प ऑटोमैटिक जेनरेट करना (Format: YYYY-MM-DDTHH:MM:SS.mmmZ)
current_utc = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

if user_id in data["users"]:
    # अगर यूजर पहले से है, तो उसका नाम बदले बिना सिर्फ स्टेटस और तारीख अपडेट होगी
    data["users"][user_id]["status"] = status_mode
    data["users"][user_id]["updated_at"] = current_utc
    print(f"✨ [Status Updated] User {user_id} set to '{status_mode}'")
else:
    # अगर नया यूजर है, तो फ्रेश रिकॉर्ड ऐड होगा
    data["users"][user_id] = {
        "username": "GE_User",
        "status": status_mode,
        "updated_at": current_utc
    }
    print(f"✨ [New User Added] User {user_id} created with status '{status_mode}'")

# फाइल को सुंदर फॉर्मेट में सुरक्षित सेव करना
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Manual execution completed successfully.")
