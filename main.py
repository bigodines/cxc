
from __future__ import print_function
import csv
import httplib2
import os
import pprint
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

pp = pprint.PrettyPrinter(indent=4)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def populate(table):
    columns = []
    with open('data/' + table + '.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')

        data = []
        for line in reader:
            data.append(line)

    columns = data[0].keys()
    cur = conn.cursor()
    str_columns = ",".join(["'" + item.replace(" ", "_") + "'" for item in columns])

    print(str_columns)
    print("--" * 40)
    cur.execute("CREATE TABLE " + table + " (" + str_columns + ") ")
    cur = conn.cursor()
    stmt = 'INSERT INTO ' + table + ' VALUES({0});'.format(','.join('?' * len(columns)))
    lines = []
    for row in data:
        line = [str(v) for v in row.values()]
        lines.append(tuple(line))

    cur.executemany(stmt, lines)


def group(row, output):
    """handmade group by order id"""
    # TODO: clean this up

    # strip at the first dash (or not)
    try:
        dash_pos = row['Item_Name'].index('-')
        trimmed = row['Item_Name'][0:dash_pos].strip()
    except:
        trimmed = row['Item_Name'].strip()

    order = row['Order_ID']
    # group items by order ID
    if output.get(order, 0) is not 0:
        full_order = output.get(order)
        full_order['items'].append(trimmed)
    else:
        # single item order
        output[order] = {'items': [trimmed]}
    return output

def format_nicely(raw_items):
    temp = {}
    for item in raw_items:
        if temp.get(item):
            temp[item] = temp[item] + 1
        else:
            temp[item] = 1

    ret = []
    for k in temp.keys():
        ret.append(" ".join([str(temp[k])]+[k]))

    return ret


def report():
    """select statements"""
    populate('orders')
    populate('orderitems')
    cur = conn.cursor()
    output = {}
    for row in cur.execute("SELECT orders.*, orderitems.Item_Name  FROM orders, orderitems WHERE orders.Order_ID = orderitems.Order_ID"):
        output = group(row, output)

    nicely = {}
    for line in output.keys():
        items = format_nicely(output[line]['items'])
        output[line]['items'] = items

        # TODO: format nicely.. items..
    pp.pprint(output)
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
    report()

conn = sqlite3.connect(':memory:')
conn.text_factory = str
conn.row_factory = dict_factory


if __name__ == '__main__':
    main()
