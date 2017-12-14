
from __future__ import print_function
import csv
import httplib2
import os
import sqlite3

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def read_orders():
    columns = []
    with open('data/orders.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')

        data = []
        for line in reader:
            data.append(line)

    columns = data[0].keys()
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    str_columns = ",".join(["'"+item.replace(" ", "_") + "'"for item in columns ])

    print(str_columns)
    cur.execute("CREATE TABLE orders ("+ str_columns +") ")
    to_db = []
    cur = conn.cursor()
    stmt = 'INSERT INTO orders VALUES({0});'.format(','.join('?' * len(columns)))
    print(stmt)
    print(line.values())
    cur.executemany(stmt, [ tuple(l) for l in [d.values() for d in data]])

    cur = conn.cursor()
    for row in cur.execute("SELECT order_id, 'hello' FROM orders"):
        print(row)
    conn.commit()

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
#     credentials = get_credentials()
#     http = credentials.authorize(httplib2.Http())
#     discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
#                     'version=v4')
#     service = discovery.build('sheets', 'v4', http=http,
#                               discoveryServiceUrl=discoveryUrl)
#
#     spreadsheetId = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
#     rangeName = 'Class Data!A2:E'
#     result = service.spreadsheets().values().get(
#         spreadsheetId=spreadsheetId, range=rangeName).execute()
#     values = result.get('values', [])
#
#     if not values:
#         print('No data found.')
#     else:
#         print('Name, Major:')
#         for row in values:
#             # Print columns A and E, which correspond to indices 0 and 4.
#             print('%s, %s' % (row[0], row[4]))
#
    orders = read_orders()
    for order in orders:
        print(order.keys())
        break

if __name__ == '__main__':
    main()

