__author__ = 'andrew.willis'

import os,sqlite3

def patcher():
    #determining root path
    rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

    #connect to database
    if os.path.isfile(rootPathVar+'/ramDatabase.db')==False:
        raise StandardError, 'error : database not found please place this patch within the same directory.'

    #create new column
    connectionVar=sqlite3.connect('ramDatabase.db')
    connectionVar.execute('ALTER TABLE ramAssetTable ADD assetDesc CHAR(50) NOT NULL')
    connectionVar.commit()
    connectionVar.close()
    return

try:
    patcher()
    print 'patch done'
except Exception as e:
    print str(e)

raw_input('Press any key to continue...')