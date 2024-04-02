#! python3
import csv, requests, json, pprint, time, sys, datetime, re, configparser, os
from threading import Timer
#################################################
## CONFIG                                      #
#################################################
config = configparser.ConfigParser()
config.read('config/config.ini')
token = config.get('auth', 'token')
header = {'Authorization': 'Bearer {}'.format(token)}
# CSVs
csv_ccotrad_source = '/Users/dan-selicaro/Documents/canvas-shells/csv/source/master_source.csv'
csv_ccotrad_output = '/Users/dan-selicaro/Documents/canvas-shells/csv/output/master_output.csv'
csv_trad_faculty = '/Users/dan-selicaro/Documents/canvas-shells/csv/source/enroll-trad-faculty.csv'
csv_source = '/Users/dan-selicaro/Documents/canvas-shells/csv/source/_CCOTRAD_2023.csv'
log_time = str(time.asctime(time.localtime(time.time())))

subs = []
terms = []

def get_subaccount_id_from_string(acct_csv):
    url = "https://champlain.instructure.com/api/v1/accounts/283/sub_accounts?per_page=100"
    payload = {"recursive": True}
    r = requests.get(url,headers=header,params=payload)
    response = r.json()
    try:
        for x in response:
            subs.append({
                "name": x["name"], "id": x["id"]
            })
        while "next" in r.links.keys():
            r = requests.get(r.links["next"]["url"], headers=header)
            response = r.json()
            for x in response:
                subs.append({
                    "name": x["name"], "id": x["id"]
                })
        for acct in subs:
            if acct["name"] == acct_csv:
                return acct["id"]
    except requests.exceptions.RequestException as e:
        print("ERROR - Check the papers.")
        print(e)
        sys.exit(1)

def get_term_id_from_string(term_csv):
    url = "https://champlain.instructure.com/api/v1/accounts/283/terms?per_page=100"
    payload = {"recursive": True}
    r = requests.get(url,headers=header,params=payload)
    response = r.json()
    pass


get_term_id_from_string()