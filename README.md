# GCP

### Google Drive API
1. Google Drive API > Enable > Create Credentials 
2. Select Google Drive API > Web Server > Application Data > No I'm not using them
3. Any name > Editor > JSON
4. Download JSON credentials > Copy client_email > Share to this email in Google Sheets

### Google Sheets API
1. Google Sheets API > Enable

### Python (gspread)
pip install gspread oauth2client

https://gspread.readthedocs.io/en/latest/

###### Get Methods:
- get_all_records()
- row_values(row)
- col_values(col)
- cell(row, col).value

###### Insert Methods:
- insert_row(array, rowNo)
- delete_row(rowNo)
- update_cell(rowNo, colNo, value)