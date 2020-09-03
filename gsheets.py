import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import pandas as pd

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("NTUDB Mock Attendance")

# Sharing worksheet
# sheet.share('shymammoth@gmail.com', perm_type='user', role='reader')

# Getting values
attendance = sheet.sheet1
data = pd.DataFrame(attendance.get_all_records())
print(data)

# Insert row
array = ["test", "test", "test", "test"]
attendance = sheet.sheet1
df = pd.DataFrame(attendance.get_all_records())
df.loc[len(df)] = array
attendance.update([df.columns.values.tolist()] + df.values.tolist())
print("Inserted: ", array)

# Getting values
attendance = sheet.sheet1
data = pd.DataFrame(attendance.get_all_records())
print(data)