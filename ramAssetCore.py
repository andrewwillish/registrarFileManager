__author__ = 'andrew.willis'

#Registrar Asset Manager - Core Module

import os, shutil, sqlite3
import xml.etree.cElementTree as ET
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
    tree=ET.parse(rootPathVar+'/root.xml')
    root=tree.getroot()
    assetRootVar=root[0].text
    assetRootVar=root[0].text
    sequenceRootVar=root[1].text
except:
    raise StandardError, 'error : failed to fetch root.xml'

#import asset to scene file
def importAsset(assetType=None,assetName=None):
    if assetType==None or assetName==None:
        cmds.confirmDialog(icn='warning',t='Error',message='No source specified', btn=['OK'])
        raise StandardError, 'error: no source specified'

    #determine root location assetRootVar and sequenceRootVar
    try:
        tree=ET.parse(rootPathVar+'/root.xml')
        root=tree.getroot()
        assetRootVar=root[0].text
    except Exception as e:
        print e
        raise StandardError, 'error : failed to fetch root.xml'

    #check if temporer namespace exist
    for chk in cmds.ls():
        if chk.find('temporer')!=-1:
            try:
                cmds.delete(chk)
            except:
                pass

    path=assetRootVar+'/'+assetType+'/'+assetName

    #select subversion
    repVar=cmds.confirmDialog(icn='question',t='Select sub-version', \
                              m='Select sub-version.',\
                              button=['MODEL','RIG','SHADER','CANCEL'])
    if repVar=='MODEL':
        importPath=path+'/model'
    elif repVar=='RIG':
        importPath=path+'/rig'
    elif repVar=='SHADER':
        importPath=path+'/shader'
    else:
        raise StandardError,'error : cancelled by user'

    for chk in os.listdir(importPath): immediateFile=chk if chk.endswith('.ma') else None
    if immediateFile==None: cmds.confirmDialog(icn='error',\
                                               t='Error',\
                                               m='There is no asset registered for model.',\
                                               button=['OK']);raise StandardError, 'error : no asset file'

    #create standard group if its not exists
    if cmds.objExists('all')==False:
        cmds.group(n='all',em=True)
        cmds.group(n='geo',em=True,p='all')
        cmds.group(n='rig',em=True,p='all')

    #file reference process
    #note: we reference the asset first to get the unique namespace implemented
    importPath=importPath+'/'+immediateFile

    if os.path.isfile(importPath)==True:
        reffFile= cmds.file(importPath,r=True,mnc=False,namespace=assetName)

        geoNode='';rigNode='';allNode='';stateCtrlNode=''
        for chk in cmds.referenceQuery(reffFile,nodes=True):
            #get geo group
            if chk.endswith(':geo'):geoNode=chk
            #get rig group
            if chk.endswith(':rig'):rigNode=chk
            #get all group
            if chk.endswith(':all'):allNode=chk
            #get All group
            if chk.endswith(':All'):allNode=chk
            #get stateCtrl group
            if chk.endswith(':stateCtrl'):stateCtrlNode=chk

        #import asset reference
        cmds.file(reffFile,ir=True)

        #find and delete geo, rig, stateCtrl, and all
        if geoNode!='':cmds.parent(geoNode,'geo')
        if rigNode!='':cmds.parent(rigNode,'rig')
        if allNode!='':cmds.delete(allNode)


        #re-parse stateCtrl
        if cmds.objExists('smoothCtrl')==False:
            cmds.group(em=True,n='smoothCtrl')
            cmds.group(em=True,n='extraCtrl')
            cmds.group('smoothCtrl','extraCtrl',n='stateCtrl')

            try:
                cmds.parent('stateCtrl','All')
            except:
                cmds.parent('stateCtrl','all')
            cmds.select('smoothCtrl')
            cmds.addAttr(ln='smoothState',k=True,at='enum',en='ON:OFF')
            cmds.addAttr(ln='smoothLevel',k=True,at='enum',en='0:1:2')

            cmds.setAttr('stateCtrl.translateX',k=False)
            cmds.setAttr('stateCtrl.translateY',k=False)
            cmds.setAttr('stateCtrl.translateZ',k=False)
            cmds.setAttr('stateCtrl.rotateX',k=False)
            cmds.setAttr('stateCtrl.rotateY',k=False)
            cmds.setAttr('stateCtrl.rotateZ',k=False)
            cmds.setAttr('stateCtrl.scaleX',k=False)
            cmds.setAttr('stateCtrl.scaleY',k=False)
            cmds.setAttr('stateCtrl.scaleZ',k=False)
            cmds.setAttr('stateCtrl.visibility',k=False)

            cmds.setAttr('smoothCtrl.translateX',k=False)
            cmds.setAttr('smoothCtrl.translateY',k=False)
            cmds.setAttr('smoothCtrl.translateZ',k=False)
            cmds.setAttr('smoothCtrl.rotateX',k=False)
            cmds.setAttr('smoothCtrl.rotateY',k=False)
            cmds.setAttr('smoothCtrl.rotateZ',k=False)
            cmds.setAttr('smoothCtrl.scaleX',k=False)
            cmds.setAttr('smoothCtrl.scaleY',k=False)
            cmds.setAttr('smoothCtrl.scaleZ',k=False)
            cmds.setAttr('smoothCtrl.visibility',k=False)

            cmds.setAttr('extraCtrl.translateX',k=False)
            cmds.setAttr('extraCtrl.translateY',k=False)
            cmds.setAttr('extraCtrl.translateZ',k=False)
            cmds.setAttr('extraCtrl.rotateX',k=False)
            cmds.setAttr('extraCtrl.rotateY',k=False)
            cmds.setAttr('extraCtrl.rotateZ',k=False)
            cmds.setAttr('extraCtrl.scaleX',k=False)
            cmds.setAttr('extraCtrl.scaleY',k=False)
            cmds.setAttr('extraCtrl.scaleZ',k=False)
            cmds.setAttr('extraCtrl.visibility',k=False)

        #Apply polySmooth
        smooth = cmds.ls(type='polySmoothFace')
        for obj in smooth :
            if cmds.isConnected( 'smoothCtrl.smoothState', obj + '.nodeState' ) == 0 :
                cmds.connectAttr( 'smoothCtrl.smoothState', obj + '.nodeState', f=True )
            else :
                print obj + " has connection"
            if cmds.isConnected( 'smoothCtrl.smoothLevel', obj + '.divisions' ) == 0 :
                cmds.connectAttr( 'smoothCtrl.smoothLevel', obj + '.divisions', f=True )
            else :
                print obj + " has connection"

        cmds.setAttr('smoothCtrl.smoothState',1)
        cmds.confirmDialog(icn='information',t='Done',m='Asset insertion done.',button=['OK'])
    else:
        cmds.confirmDialog(icn='information',t='Error',m='File not found.',button=['OK'])
    return

#delete record
def deleteAsset(assetId=None):
    #connect to database
    try:
        connectionVar=sqlite3.connect(rootPathVar+'/ramDatabase.db')
    except:
        raise StandardError,'error : failed to connect to database'

    if assetId==None: raise StandardError, 'error : no asset id specified'

    #get asset path
    assetPath=connectionVar.execute("SELECT * FROM ramAssetTable WHERE assetId='"+str(assetId)+"'").fetchall()

    if len(assetPath)==1:
        assetPath=assetPath[0]
        #delete file in server
        try:
            shutil.rmtree(str(assetPath[4]))
        except WindowsError:
            pass

        #incuring to database
        connectionVar.execute("DELETE FROM ramAssetTable WHERE assetId='"+str(assetId)+"'")
        connectionVar.commit()
    return

#rename asset
def renameAsset(assetId=None, newAssetName=None):
    #connect to database
    try:
        connectionVar=sqlite3.connect(rootPathVar+'/ramDatabase.db')
    except:
        raise StandardError,'error : failed to connect to database'

    #check asset id specification
    if assetId==None and newAssetName==None:raise StandardError, 'error : incomplete data specified'

    #get record
    dataRecord=connectionVar.execute("SELECT * FROM ramAssetTable WHERE assetId='"+str(assetId)+"'").fetchall()
    if len(dataRecord)!=1: raise StandardError, 'error : anomaly database reply'

    #generate new path data
    dataRecord=dataRecord[0]

    oldPath=dataRecord[4]
    newPath=oldPath[:oldPath.rfind('/')+1]+newAssetName

    #rename newpath data
    try:
        os.rename(oldPath,newPath)
    except Exception as e:
        print str(e)
        raise StandardError, 'error : rename error'

    #incurring to database
    connectionVar.execute("UPDATE ramAssetTable SET assetName='"+str(newAssetName)+"', assetLocationPath='"+str(newPath)+"' WHERE assetId='"+str(assetId)+"'")
    connectionVar.commit()
    connectionVar.close()
    return

#list all notes
def listAssetNotes():
    #connect to database
    try:
        connectionVar=sqlite3.connect(rootPathVar+'/ramDatabase.db')
    except:
        raise StandardError,'error : failed to connect to database'
    assetLis=connectionVar.execute("SELECT * FROM ramAssetNotesTable")
    assetLis=assetLis.fetchall()
    connectionVar.close()
    return assetLis

def postNewNotes(title=None,author=None,message=None, assetId=None,assetName=None):
    if title==None or author==None or message==None or assetId==None:
        raise StandardError, 'error : insufficient data specified'

    #connect to database
    try:
        connectionVar=sqlite3.connect(rootPathVar+'/ramDatabase.db')
    except:
        raise StandardError,'error : failed to connect to database'

    connectionVar.execute("INSERT INTO ramAssetNotesTable (notesTitle, notesAuthor, notesMessage,assetId)"\
        "VALUES ("\
        "'"+str(title)+"',"\
        "'"+str(author)+"',"\
        "'"+str(message)+"',"\
        "'"+str(assetId)+"')")
    connectionVar.commit()

    connectionVar.close()

    #log record
    ramRecordLog(assetName=str(assetName),assetOperation='assetRegistration',user=currentUserVar,\
                 assetDescription='title:'+str(title)+',assetId:'+str(assetId))
    return

#List all log record from database
def listLogTable():
    #connect to database
    try:
        connectionVar=sqlite3.connect(rootPathVar+'/ramDatabase.db')
    except:
        raise StandardError,'error : failed to connect to database'
    logLis=connectionVar.execute("SELECT * FROM ramAssetLog")
    logLis=logLis.fetchall()
    connectionVar.close()
    return logLis

#List all asset record from database
def listAssetTable():
    #connect to database
    try:
        connectionVar=sqlite3.connect(rootPathVar+'/ramDatabase.db')
    except:
        raise StandardError,'error : failed to connect to database'
    assetLis=connectionVar.execute("SELECT * FROM ramAssetTable")
    assetLis=assetLis.fetchall()
    connectionVar.close()
    return assetLis

#register new asset record (this function will not upload anything to server just create a record of a new asset)
def registerAssetRecord(name=None, keyword=None, type=None, description=None):
    if name==None and keyword==None and type==None:raise StandardError, 'error : insufficient data specified'
    if name==None or name=='':raise StandardError, 'error : name not specified'
    if type==None or type=='':raise StandardError, 'error : asset type not specified'
    if description==None: raise StandardError, 'error : asset description is not set'

    #connect to database
    try:
        connectionVar=sqlite3.connect(rootPathVar+'/ramDatabase.db')
    except:
        raise StandardError,'error : failed to connect to database'

    #parsing type [0]=CHAR [1]=PROP [2]=SETS
    if type==0:
        type='CHAR'
    elif type==1:
        type='PROP'
    elif type==2:
        type='SETS'
    else:
        raise StandardError, 'error : invalid type specified'

    #determine asset location
    assetLocation=assetRootVar+'/'+str(type)+'/'+str(name)

    #creating asset directory tree
    if os.path.isdir(assetLocation)==False:
        os.makedirs(assetLocation)
        os.makedirs(assetLocation+'/model')
        os.makedirs(assetLocation+'/rig')
        os.makedirs(assetLocation+'/texture')
        os.makedirs(assetLocation+'/shader')
        os.makedirs(assetLocation+'/_legacy/model')
        os.makedirs(assetLocation+'/_legacy/rig')
        os.makedirs(assetLocation+'/_legacy/shader')

    #inserting to database
    connectionVar.execute("INSERT INTO ramAssetTable (assetName, assetType, assetKeyword,"\
        "assetLocationPath, assetModelled, assetShaded,assetRigged,assetDesc) VALUES "\
        "('"+str(name)+"',"\
        "'"+str(type)+"',"\
        "'"+str(keyword)+"',"\
        "'"+str(assetLocation)+"',"\
        "0,"\
        "0,"\
        "0,"\
        "'"+str(description)+"')")
    connectionVar.commit()
    connectionVar.close()

    #log record
    ramRecordLog(assetName=str(name),assetOperation='assetRegistration',user=currentUserVar,\
                 assetDescription='assetName:'+str(name)+',assetType:'+str(type))
    return

#update asset record. This function will not affect maya file operation.
def updateAssetRecord(name=None,keyword=None,modelStat=None,shaderStat=None,rigStat=None,description=None):
    if name==None:raise StandardError, 'error : no name specified'

    #connect to database
    try:
        connectionVar=sqlite3.connect(rootPathVar+'/ramDatabase.db')
    except:
        raise StandardError,'error : failed to connect to database'

    #generating sql instruction
    execStringVar="UPDATE ramAssetTable SET"
    log=''
    if keyword!=None:
        execStringVar=execStringVar+" assetKeyword='"+str(keyword)+"',"
        log=log+'keyword:'+str(keyword)+','
    if modelStat!=None:
        execStringVar=execStringVar+" assetModelled='"+str(modelStat)+"',"
        log=log+'modelStat:'+str(modelStat)+','
    if shaderStat!=None:
        execStringVar=execStringVar+" assetShaded='"+str(shaderStat)+"',"
        log=log+'shaderStat:'+str(shaderStat)+','
    if rigStat!=None:
        execStringVar=execStringVar+" assetRigged='"+str(rigStat)+"',"
        log=log+'rigStat:'+str(rigStat)+','
    if description!=None:
        execStringVar=execStringVar+" assetDesc='"+str(description)+"',"
        log=log+'description:'+str(description)+','

    if execStringVar.endswith(','):
        execStringVar=execStringVar[:execStringVar.rfind(',')]
    execStringVar=execStringVar+" WHERE assetName='"+str(name)+"'"

    if log.endswith(','):
        log=log[:log.rfind(',')]

    #executing sql instruction
    connectionVar.execute(execStringVar)
    connectionVar.commit()

    connectionVar.close()

    #log record
    ramRecordLog(assetName=str(name),assetOperation='assetUpdateRecord',user=currentUserVar,\
                 assetDescription=str(log))
    return

#upload an asset to server. it is advisable to pair this operation with updateRecord
def uploadAsset(name=None, assetType=None, assetTarget=None):
    if name==None:
        raise StandardError, 'error : no asset name specified'
    if assetType==None or assetTarget==None:
        raise StandardError, 'error : no asset type or target specified'

    #parsing type [0]=CHAR [1]=PROP [2]=SETS
    if assetType==0:
        assetType='CHAR'
        prefixVar='c_'
    elif assetType==1:
        assetType='PROP'
        prefixVar='p_'
    elif assetType==2:
        assetType='SETS'
        prefixVar='s_'
    else:
        raise StandardError, 'error : invalid type specified'

    #upload procedure
    currentFileLocation=cmds.file(q=True, sn=True)

    #check if local workspace exists
    workspaceVar = str(os.environ['WINDIR']).replace('\\Windows','')+'/workspace'

    if os.path.isdir(workspaceVar)==False:
        os.makedirs(workspaceVar)

    #preparing saving path
    #determining timestamp
    date=datetime.datetime.now()
    year=date.year
    month=date.month
    day=date.day
    hour=date.hour
    minutes=date.minute
    second=date.second
    timeStampVar='['+str(year)+'-'+str(month)+'-'+str(day)+']('+str(hour)+','+str(minutes)+','+str(second)+')'

    #preparing asset file stamp
    localFileSavePathVar=str(workspaceVar)+'/'+str(prefixVar)+str(name)+timeStampVar+'.ma'
    serverFileSavePathVar=str(assetRootVar)+'/'+str(assetType)+'/'+str(name)+'/'+str(assetTarget)+'/'+str(prefixVar)+str(name)+'.ma'
    legacyFileSavePathVar=str(assetRootVar)+'/'+str(assetType)+'/'+str(name)+'/_legacy/'+str(assetTarget)+'/'+str(prefixVar)+str(name)+timeStampVar+'.ma'
    textureSavePathVar=str(assetRootVar)+'/'+str(assetType)+'/'+str(name)+'/texture'

    #saving and remap texture file to server instruction
    for chk in cmds.ls(type='file'):
        oldFileNameVar=cmds.getAttr(chk+'.fileTextureName')
        newFileNameVar=textureSavePathVar+'/'+oldFileNameVar[oldFileNameVar.rfind('/')+1:]
        if oldFileNameVar!=newFileNameVar:
            try:
                shutil.copy(oldFileNameVar,newFileNameVar)
            except:
                pass
        cmds.setAttr(chk+'.fileTextureName',newFileNameVar,type='string')

    #saving operation
    #saving to local
    if cmds.file(q=True,sn=True)=='':
        cmds.file(rename=localFileSavePathVar)
        cmds.file(save=True,f=True)
    else:
        localFileSavePathVar=cmds.file(q=True,sn=True)
        cmds.file(s=True)

    #saving to server
    #note: check if there is already a previous file. if there is then do archiving instruction
    if os.path.isfile(serverFileSavePathVar):
        #There is already a file here. archiving
        shutil.copy(serverFileSavePathVar,legacyFileSavePathVar)

        #save file to server
        cmds.file(rename=serverFileSavePathVar)
        cmds.file(save=True, f=True)
    else:
        #save file directly to server
        cmds.file(rename=serverFileSavePathVar)
        cmds.file(save=True, f=True)

    #reopen local file
    cmds.file(localFileSavePathVar,o=True,f=True)

    #log record
    ramRecordLog(assetName=str(name),assetOperation='assetUpload',user=currentUserVar,\
                 assetDescription='assetName:'+str(name)+',assetType:'+str(assetType)+',assetTarget='+str(assetTarget))
    return

def downloadAsset(name=None, assetType=None, assetTarget=None):
    if name==None:raise StandardError, 'error : no asset name specified'
    if assetType==None or assetTarget==None: raise StandardError, 'error : no asset type or target specified'
    if assetTarget==None or assetTarget=='': raise StandardError, 'error : no asset target specified'
    print 'tessssssssssssssssssst'
    #parsing type [0]=CHAR [1]=PROP [2]=SETS
    if assetType==0:
        assetType='CHAR'
        prefixVar='c_'
    elif assetType==1:
        assetType='PROP'
        prefixVar='p_'
    elif assetType==2:
        assetType='SETS'
        prefixVar='s_'
    else:
        raise StandardError, 'error : invalid type specified'

    #check if local workspace exists
    workspaceVar = str(os.environ['WINDIR']).replace('\\Windows','')+'/workspace'
    if os.path.isdir(workspaceVar)==False:os.makedirs(workspaceVar)

    #preparing saving path
    #determining timestamp
    date=datetime.datetime.now()
    year=date.year
    month=date.month
    day=date.day
    hour=date.hour
    minutes=date.minute
    second=date.second
    timeStampVar='['+str(year)+'-'+str(month)+'-'+str(day)+']('+str(hour)+','+str(minutes)+','+str(second)+')'

    #preparing asset file stamp
    localFilePathVar=str(workspaceVar)+'/'+str(prefixVar)+str(name)+timeStampVar+'.ma'
    serverFilePathVar=str(assetRootVar)+'/'+str(assetType)+'/'+str(name)+'/'+str(assetTarget)+'/'+str(prefixVar)+str(name)+'.ma'
    serverFileDirVar=str(assetRootVar)+'/'+str(assetType)+'/'+str(name)+'/'+str(assetTarget)
    legacyFileDirVar=str(assetRootVar)+'/'+str(assetType)+'/'+str(name)+'/_legacy/'+str(assetTarget)

    #load procedure. copy file server to local then open the local version
    if os.path.isfile(serverFilePathVar)==False:
        raise StandardError, 'error : server file did not exists'
    shutil.copy(serverFilePathVar,localFilePathVar)
    cmds.file(localFilePathVar,o=True,f=True)

    #log record
    ramRecordLog(assetName=str(name),assetOperation='assetDownload',user=currentUserVar,\
                 assetDescription='assetName:'+str(name)+',assetType:'+str(assetType)+',assetTarget='+str(assetTarget))
    return

def downloadAssetLegacy(name=None, assetType=None, assetTarget=None):
    if name==None:raise StandardError, 'error : no asset name specified'
    if assetType==None or assetTarget==None:raise StandardError, 'error : no asset type or target specified'
    if assetTarget==None or assetTarget=='':raise StandardError, 'error : no asset target specified'

    #parsing type [0]=CHAR [1]=PROP [2]=SETS
    if assetType==0:
        assetType='CHAR'
        prefixVar='c_'
    elif assetType==1:
        assetType='PROP'
        prefixVar='p_'
    elif assetType==2:
        assetType='SETS'
        prefixVar='s_'
    else:
        raise StandardError, 'error : invalid type specified'

    #check if local workspace exists
    workspaceVar = str(os.environ['WINDIR']).replace('\\Windows','')+'/workspace'

    #preparing saving path
    #determining timestamp
    date=datetime.datetime.now()
    year=date.year
    month=date.month
    day=date.day
    hour=date.hour
    minutes=date.minute
    second=date.second
    timeStampVar='['+str(year)+'-'+str(month)+'-'+str(day)+']('+str(hour)+','+str(minutes)+','+str(second)+')'

    #determining assetName. due to name now contain timestamp an assetname is necessary to point out individual
    #asset root folder

    assetName=name[name.find('_')+1:name.find('[')]

    #preparing asset file stamp
    localFilePathVar=str(workspaceVar)+'/'+str(prefixVar)+str(assetName)+timeStampVar+'.ma'
    serverFilePathVar=str(assetRootVar)+'/'+str(assetType)+'/'+str(assetName)+'/_legacy/'+str(assetTarget)+'/'+str(name)+'.ma'

    #open file
    shutil.copy(serverFilePathVar,localFilePathVar)
    cmds.file(localFilePathVar,o=True,f=True)

    #logger
    ramRecordLog(assetName=str(name),assetOperation='assetDownloadLegacy',user=currentUserVar,\
                 assetDescription='assetName:'+str(name)+',assetType:'+str(assetType)+',assetTarget='+str(assetTarget))

    return

def listAssetLegacyFiles(name=None):
    #connect to database
    try:
        connectionVar=sqlite3.connect(rootPathVar+'/ramDatabase.db')
    except:
        raise StandardError,'error : failed to connect to database'

    recordVar=connectionVar.execute("SELECT * FROM ramAssetTable WHERE assetName='"+str(name)+"'")
    recordVar=recordVar.fetchall()
    if len(recordVar)>2:raise StandardError, 'error : sqlite output anomaly'
    if recordVar==[]:raise StandardError, 'error : no record found'
    assetPathVar=recordVar[0][4]
    if os.path.isdir(assetPathVar)==False:raise StandardError, 'error : asset file non exists'

    modelLegacyPath=assetPathVar+'/_legacy/model'
    shaderLegacyPath=assetPathVar+'/_legacy/shader'
    rigLegacyPath=assetPathVar+'/_legacy/rig'

    allLis=[]
    allLis.append(os.listdir(modelLegacyPath))
    allLis.append(os.listdir(shaderLegacyPath))
    allLis.append(os.listdir(rigLegacyPath))

    connectionVar.close()
    return allLis

def ramRecordLog(assetName=None, assetOperation=None, assetDescription=None, user=None):
    if assetName==None or assetOperation==None or assetDescription==None:
        raise StandardError, 'error : insufficitent credential submitted'

    #connect to database
    try:
        connectionVar=sqlite3.connect(rootPathVar+'/ramDatabase.db')
    except:
        raise StandardError,'error : failed to connect to database'

    connectionVar.execute("INSERT INTO ramAssetLog (logAssetName,logUser, logOperation, logDescription)"\
        "VALUES ('"+str(assetName)+"','"+str(user)+"','"+str(assetOperation)+"','"+str(assetDescription)+"')")
    connectionVar.commit()
    connectionVar.close()
    return