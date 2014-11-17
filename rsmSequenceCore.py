__author__ = 'andrew.willis'

import os, shutil, sqlite3
import xml.etree.cElementTree as ET
import asiist
try:
    import maya.cmds as cmds
except:
    pass
import datetime
import getpass

#determin current user
currentUserVar=str(getpass.getuser())

#determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#determine root location assetRootVar and sequenceRootVar
try:
    tree=ET.parse(rootPath+'/root.xml')
    root=tree.getroot()
    assetRootVar=root[0].text
    sequenceRootVar=root[1].text
except:
    raise StandardError, 'error : failed to fetch root.xml'

def listEps():
    print rootPathVar
    return