# GCP

### Google Drive API
1. Google Drive API > Enable > Create Credentials 
2. Select Google Drive API > Web Server > Application Data > No I'm not using them
3. Any name > Editor > JSON
4. Download JSON credentials > Copy client_email > Share to this email in Google Sheets

### Google Sheets API
1. Google Sheets API > Enable

### Python (gspread)

https://gspread.readthedocs.io/en/latest/

sudo yum update -y 

sudo amazon-linux-extras install python3.8

alias python3='/usr/bin/python3.8'

python3 --version

sudo yum install git -y

sudo yum -y install python3-pip

git clone https://github.com/tonyngmk/telegram-ntudb-bot.git

cd telegram-ntudb-bot

chmod 755 ./bot.py

python3 -m pip install --user python-telegram-bot

python3 -m pip install --user gspread oauth2client

python3 -m pip install --user pandas

screen

ctrl + a + c (create new screen)

ctrl + a + n (switch screens)

python3 bot.py

###### Get Methods:
- get_all_records()
- row_values(row)
- col_values(col)
- cell(row, col).value

###### Insert Methods:
- insert_row(array, rowNo)
- delete_row(rowNo)
- update_cell(rowNo, colNo, value)