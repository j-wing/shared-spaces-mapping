from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import pprint
import json
import time

from geopy.geocoders import GoogleV3, Nominatim
# from models import Document, Requestor


def get_secrets():
    with open("apikey.txt") as f:
        return [l.strip() for l in f.readlines()]


(API_KEY, URL, SHEET_ID) = get_secrets()

API_KEY = open("apikey.txt").read().strip()
goog_geolocator = GoogleV3(API_KEY)
JSON_NAME = "entries.json"


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
RANGE = "Restaurants!A:I"


def build_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('sheets', 'v4', credentials=creds)


def get_business_list():
    sheet = build_service().spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE).execute()
    return result['values']


def run():
    biz = get_business_list()
    with open("entries.json", "r") as f:
        geocoded = json.load(f)
        try:
            for b in biz:
                if not b:
                    continue
                key = "%s-%s" % (b[0], b[1])
                if key in geocoded:
                    continue

                print("Geocoding", key)

                loc = goog_geolocator.geocode(
                    "%s %s, San francisco, CA, USA" % (b[0], b[1]), components=('locality', 'San Francisco, CA'))
                geocoded[key] = {
                    'location': loc.raw,
                    'sheet_value': b
                }
                time.sleep(.5)
        # except (KeyboardInterrupt, Exception) as e:
        finally:
            with open('entries.json', 'w') as f:
                json.dump(geocoded, f)

    # df = gen_df()
    # results = get_existing_entries(target_dir)

    # skipped = []
    # for row in df:
    #     if row['record'] not in results or regen:
    #         if row['hearing_date'] != "":
    #             row['hearing_date'] = dateparser.parse(
    #                 row['hearing_date'], settings={'TIMEZONE': time.tzname[time.daylight]}).isoformat()

    #         if row['record'] in results and 'location' in results[row['record']] and not regen_location:
    #             row['location'] = results[row['record']]['location']
    #         else:
    #             try:
    #                 print("running geocoder!", fix_addr(row['addr']))
    #                 loc = goog_geolocator.geocode(
    #                     fix_addr(row['addr']) + ", San francisco, CA, USA", components=('locality', 'San Francisco, CA'))
    #                 # loc = geolocator.geocode(
    #                 #     fix_addr(row['addr']) + ", San Francisco, CA, USA", addressdetails=True)
    #                 if loc is not None:
    #                     row['location'] = loc.raw
    #                 else:
    #                     skipped.append(fix_addr(row['addr']))
    #                     continue
    #             except Exception as e:
    #                 addr = fix_addr(row['addr'])
    #                 print("Got an error trying to get the location for",
    #                       addr, ": ", e)
    #                 skipped.append(addr)
    #                 continue
    #     else:
    #         row = results[row['record']]
    #         # row['location'] = {}
    #     result = row.copy()
    #     if "DRP" in row['type']:
    #         result.update(handle_dr(target_dir, row['record'], local))
    #     results[row['record']] = result
    # print("Skipped:", skipped)

    # print("Checking for new DR data...")
    # for id, row in results.items():
    #     if "DRP" in row['type']:
    #         results[id].update(handle_dr(target_dir, id, local))

    # fname = os.path.join(target_dir, JSON_NAME)
    # with open(fname, 'w') as f:
    #     json.dump(results, f, sort_keys=True, indent=1)
    #     print("output to", fname)


if __name__ == "__main__":
    # args = parser.parse_args()
    run()
