
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


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def populate(table):
    columns = []
    with open('data/'+table+'.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')

        data = []
        for line in reader:
            data.append(line)

    columns = data[0].keys()
    cur = conn.cursor()
    str_columns = ",".join(["'" + item.replace(" ", "_") + "'" for item in columns ])

    print(str_columns)
    print("--" * 40)
    cur.execute("CREATE TABLE "+table+" ("+ str_columns +") ")
    cur = conn.cursor()
    stmt = 'INSERT INTO '+table+' VALUES({0});'.format(','.join('?' * len(columns)))
    lines = []
    for row in data:
        line = [str(v) for v in row.values()]
        lines.append(tuple(line))

    cur.executemany(stmt, lines)




def load_data():
    populate('orders')
    populate('orderitems')
    cur = conn.cursor()
    output = {}
    for row in cur.execute("SELECT orders.*, orderitems.Item_Name  FROM orders, orderitems WHERE orders.Order_ID = orderitems.Order_ID SORT BY orders.Order_ID"):
        # TODO: optimize scanning since items are ordered by order ID
        # group items by order ID
        if
        # trim at the first dash (or not)
        dash_pos = row['Item_Name'].index('-')
        if dash_pos > 0:
            trimmed = row['Item_Name'][0:dash_pos]
        else:
            trimmed = row['Item_Name']
        line = [row['Order_ID'], row['Sale_Date'], trimmed, row['Full_Name']]
        print(line)
        pass
        #print(row)
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
    orders = load_data()
#    for order in orders: print(order.keys())
#        break

conn = sqlite3.connect(':memory:')
conn.text_factory = str
conn.row_factory = dict_factory


if __name__ == '__main__':
    main()

