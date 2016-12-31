#!/usr/bin/python

import re
import sys
import csv
import sqlite3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('document', help='Location of Banktivity document')
parser.add_argument('--account', required=True)
parser.add_argument('--search')
args = parser.parse_args()

db = sqlite3.connect("file:" + args.document + "?mode=ro")
csv_writer = csv.writer(sys.stdout)

id = db.execute('SELECT z_pk FROM zaccount WHERE zname=? AND zfinancialaccount=1', (args.account, ))
try:
    params = (id.next()[0],)
except:
    raise Exception("Couldn't find account called '%s'" % args.account)

if args.search is not None:
    params += ('%' + args.search + '%',)
else:
    params += ('%',)

result = db.execute('''SELECT date(t.zdate, 'unixepoch', '+31 years') AS DATE,
  li.zamount, t.ztitle, li.zmemo, t.znote, t.zcleared --, '....', *
  FROM zlineitem li
  JOIN ztransaction t ON li.ztransaction = t.z_pk
  WHERE zaccount=?
  AND t.ztitle LIKE ?
  ORDER BY date''', params)


csv_writer.writerow([re.sub('^Z', '', x[0]).lower() for x in result.description])
for row in result:
    csv_writer.writerow(row)
