# NTUDB Attendance Telegram Bot
Search `@NTUDB_Bot` in Telegram. 

Created to ease weekly copy-paste troubles. Users can indicate and query attendance without spamming main chat groups.

This can be an example of seamlessly integrating **Telegram** with **Google Sheets**.

## Diagram

*insert diagram here*

### 1. Google Cloud Platform (GCP)

#### 1.1 Google Drive API

Steps to obtain credentials for Google Drive API:
1. Google Drive API > Enable > Create Credentials 
2. Select Google Drive API > Web Server > Application Data > No I'm not using them
3. Any name > Editor > JSON
4. Download JSON credentials > Copy client_email > Share to this email in Google Sheets

### 1.2 Google Sheets API

Integrating Drive with Sheets
- Google Sheets API > Enable

### 2. Python 

python-telegram-bot is used to talk from python-telegram, gspread is used to talk from python-(google spreadsheet)

#### 2.1 Python-Google Spreadsheet

	python3 -m pip install --user gspread oauth2client

References: https://gspread.readthedocs.io/en/latest/

In essence, the bot is able to query and insert rows to gsheets directly.

###### Get Methods:
- get_all_records()
- row_values(row)
- col_values(col)
- cell(row, col).value

###### Insert Methods:
- insert_row(array, rowNo)
- delete_row(rowNo)
- update_cell(rowNo, colNo, value)

####### Sheets active in bot:
- Users
- Attendance

#### 2.2 Python-Telegram

	python3 -m pip install --user python-telegram-bot

Thereafter, just edit along **bot.py** file and execute it. The python script must continually run for the bot to work. 
To do so, one can run it perpetually using a cloud virtual machine, e.g. AWS EC2, Google Compute Engine, etc. 

I've tried running on free tier t2 micro and the CPU Credit Usage for 2 bots is negligible, so it should be essentially free.

<p align="center">
  <img src="https://raw.githubusercontent.com/tonyngmk/my-stoic-telebot/master/cpu_cred_usage.png" />
</p>


##### Dump of codes to get it hosted on AWS EC2 Linux2 AMI:

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

### Note

This git repo does not have certain files containing credentials excluded in .gitignore. In case you are reusing the script, store:
- Telegram bot's API as **botapi.txt**
- Google Drive API as **creds.json**
