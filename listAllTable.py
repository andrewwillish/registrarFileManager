__author__ = 'andrew.willis'

import sqlite3

conn=sqlite3.connect('ramDatabase.db')

for chk in conn.execute("SELECT * FROM ramAssetTable").fetchall():print chk