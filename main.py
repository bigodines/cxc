
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


def format_nicely(row, output):
    """format fields in a row for display."""
    # TODO: clean this up

    # strip at the first dash (or not)
    dash_pos = row['Item_Name'].index('-')
    if dash_pos > 0:
        trimmed = row['Item_Name'][0:dash_pos].strip()
    else:
        trimmed = row['Item_Name'].strip()
    line = [row['Order_ID'], row['Sale_Date'], trimmed, row['Full_Name']]
    order = row['Order_ID']
    # group items by order ID
    if output.get(order, 0) is not 0:
        # TODO: escape
        base_regexp = "(d+) " + trimmed
        old_order = output.get(order)
        new_order = []
        for i, item in enumerate(old_order):
            pp.pprint(item)
            import re
            pp.pprint(item)
            found = re.search(base_regexp, item)
            if found:
                count = found.group(0)
                new_order.append(str(int(count) + 1) + " " + trimmed)
            else:
#                old_order.append("1 " + trimmed)
                pass

        output[order].append(trimmed)
        print(output.get(order))
    else:
        output[order] = ["1 " + trimmed]

    return output



def report():
    """select statements"""
    populate('orders')
    populate('orderitems')
    cur = conn.cursor()
    output = {}
    for row in cur.execute("SELECT orders.*, orderitems.Item_Name  FROM orders, orderitems WHERE orders.Order_ID = orderitems.Order_ID"):
        output = format_nicely(row, output)

    pp.pprint(output)
    # print(output)
    # print(row)
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
