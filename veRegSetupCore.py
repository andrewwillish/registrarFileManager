__author__ = 'andrew.willis'

#Registrar Asset Manager - Setup Core
#Andrew Willis 2014

#import module
import sqlite3, shutil, os, shutil
import xml.etree.cElementTree as ET

#Determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

def setupAssetNotes():
    global connectionVar, rootPathVar

    #Setup main database called ramDatabase.db
    if os.path.isfile(rootPathVar+'/ramDatabase.db')==False:
        connectionVar=sqlite3.connect('ramDatabase.db')

    try:
        connectionVar=sqlite3.connect('ramDatabase.db')
        connectionVar.execute("CREATE TABLE ramAssetNotesTable"\
            "(notesId INTEGER PRIMARY KEY AUTOINCREMENT,"\
            "assetId CHAR(50) NOT NULL,"\
            "notesTitle CHAR(50) NOT NULL UNIQUE,"\
            "notesAuthor CHAR(50) NOT NULL,"\
            "notesDate DATETIME DEFAULT CURRENT_TIMESTAMP,"\
            "notesMessage CHAR(50) NOT NULL)")
        connectionVar.commit()
        returnVar=1
    except Exception as e:
        print str(e)
        returnVar=0
    return returnVar

def setupAssetTable():
    global connectionVar, rootPathVar

    #Setup main database called ramDatabase.db
    if os.path.isfile(rootPathVar+'/ramDatabase.db')==False:
        connectionVar=sqlite3.connect('ramDatabase.db')

    try:
        connectionVar=sqlite3.connect('ramDatabase.db')
        connectionVar.execute("CREATE TABLE ramAssetTable"\
            "(assetId INTEGER PRIMARY KEY AUTOINCREMENT,"\
            "assetName CHAR(50) NOT NULL UNIQUE,"\
            "assetType CHAR(50) NOT NULL,"\
            "assetKeyword CHAR(50) NOT NULL,"\
            "assetLocationPath CHAR(50) NOT NULL,"\
            "assetModelled CHAR(50) NOT NULL,"\
            "assetShaded CHAR(50) NOT NULL,"\
            "assetRigged CHAR(50) NOT NULL,"\
            "assetDesc CHAR(50) NOT NULL)")
        connectionVar.commit()
        returnVar=1
    except Exception as e:
        print str(e)
        returnVar=0
    return returnVar

def setupLogTable():
    global connectionVar, rootPathVar

    #Setup main database called ramDatabase.db
    if os.path.isfile(rootPathVar+'/ramDatabase.db')==False:
        connectionVar=sqlite3.connect('ramDatabase.db')

    #Log notes
    #logId=log record id given by database
    #logAssetId=id from affected asset record [assetId]
    #logModule=module
    #logOperation=operation that has been done
    #logDescription=extra description for the log file

    try:
        connectionVar=sqlite3.connect('ramDatabase.db')
        connectionVar.execute("CREATE TABLE ramAssetLog"\
            "(logId INTEGER PRIMARY KEY AUTOINCREMENT,"\
            "logUser CHAR(50) NOT NULL,"\
            "logAssetName CHAR(50) NOT NULL,"\
            "logOperation CHAR(50) NOT NULL,"\
            "logDescription CHAR(50) NOT NULL,"\
            "notesDate DATETIME DEFAULT CURRENT_TIMESTAMP)")
        connectionVar.commit()
        returnVar=1
    except Exception as e:
        print str(e)
        returnVar=0
    return returnVar

def setupRootXml():
    global connectionVar, rootPathVar
    #make root.xml. create one if not exist
    if os.path.isfile(rootPathVar+'/root.xml')==False:
        root=ET.Element('root')

        assetRoot=ET.SubElement(root,'assetRoot')
        assetRoot.text=''

        sequencialRoot=ET.SubElement(root,'sequencialRoot')
        sequencialRoot.text=''

        systemRoot=ET.SubElement(root,'systemRoot')
        systemRoot.text=''

        tree=ET.ElementTree(root)
        tree.write(rootPathVar+'/root.xml')
        returnVar=1
    else:
        returnVar=0
    return returnVar

def setRootPath( assetRootPath=None, sequencialRootPath=None):
    global connectionVar, rootPathVar
    #validate path
    if assetRootPath==None and sequencialRootPath==None:
        raise  StandardError, 'error : none root path specified'

    #processing asset root
    if assetRootPath!=None:
        if assetRootPath.endswith('/'):
            assetRootPath=assetRootPath[:assetRootPath.rfind('/')]
        #make asset root directory. invoke error if access is denied
        try:
            if os.path.isdir(assetRootPath)==False:
                os.makedirs(assetRootPath)
        except:
            raise StandardError, 'error : asset root unable to create directory'

        try:
            #Writing asset root [0]=asset root, [1]=sequencial root
            tree=ET.parse(rootPathVar+'/root.xml')
            root=tree.getroot()

            root[0].text=str(assetRootPath)
            tree=ET.ElementTree(root)
            tree.write(rootPathVar+'/root.xml')
        except Exception as e:
            raise StandardError, 'error : '+str(e)

    #processing sequencial root
    if sequencialRootPath!=None:
        if sequencialRootPath.endswith('/'):
            sequencialRootPath=sequencialRootPath[:sequencialRootPath.rfind('/')]
        #make sequencial root directory. invoke error if access is denied
        try:
            if os.path.isdir(sequencialRootPath)==False:
                os.makedirs(sequencialRootPath)
        except:
            raise StandardError, 'error : asset root unable to create directory'

        try:
            #Writing asset root [0]=asset root, [1]=sequencial root
            tree=ET.parse(rootPathVar+'/root.xml')
            root=tree.getroot()

            root[1].text=str(sequencialRootPath)
            tree=ET.ElementTree(root)
            tree.write(rootPathVar+'/root.xml')
        except Exception as e:
            raise StandardError, 'error : '+str(e)
    return
