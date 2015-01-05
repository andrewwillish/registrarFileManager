__author__ = 'andrew.willis'

#MNC Registrar Core Module
#Andrew Willis

#import module
import os, shutil, sqlite3
import xml.etree.cElementTree as ET
import datetime, getpass
try:
    import maya.cmds as cmds
    import maya.mel as mel
    import pymel.core as pc
except:
    pass
try:
    import maya.OpenMaya as api
    import maya.OpenMayaUI as apiUI
    import asiist
except:
    print '<external module access 3 modules skipped>'

#cutom error declaration
class registrarError(Exception):
    def __init__(self, text):
        self.text = text
    def __str__(self):
        return repr(self.text)

#get initial credential
CURRENT_USER = str(getpass.getuser())
SCRIPT_ROOT = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')
WIN_ROOT = os.environ['ProgramFiles'][:2]+'/'

#determine root location assetRoot and sequenceRoot
if not os.path.isfile(SCRIPT_ROOT+'/root.xml'): raise registrarError, 'root.xml not exists'
root = (ET.parse(SCRIPT_ROOT+'/root.xml')).getroot()
ASSET_ROOT = root[0].text
SEQUENCE_ROOT = root[1].text

#get project name and project code from asiist
for chk in asiist.getEnvi():
    if chk[0] == 'projName': PRJ_NAME = chk[1]
    if chk[0] == 'projCode': PRJ_CODE = chk[1]
    if chk[0] == 'resWidth': PLB_RESWIDTH = chk[1]
    if chk[0] == 'resHeight': PLB_RESHEIGHT = chk[1]
    if chk[0] == 'playblastCodec': PLB_CODEC = chk[1]
    if chk[0] == 'playblastFormat': PLB_FORMAT = chk[1]
    if chk[0] == 'unit': PRJ_UNIT = chk[1]

#determine timestamp function return timestamp
def timestamp():
    date = datetime.datetime.now(); year = date.year;month = date.month; day = date.day
    hour = date.hour; minutes = date.minute; second = date.second
    return '['+str(day)+','+str(month)+','+str(year)+']('+str(hour)+','+str(minutes)+','+str(second)+')'

#read assetType.xml data
try:
    tree = ET.parse(SCRIPT_ROOT+'/assetType.xml')
    root = tree.getroot()
    ASSET_TYPES = []
    for chk in root:
        ASSET_TYPES.append({'tag':str(chk.tag), 'desc':str(chk.text)})
except Exception as e:
    cmds.confirmDialog(icn='warning', t='error', m=str(e), button=['OK'])
    raise registrarError, 'failed to fetch assetType.xml'

#generate data path
def genDataPath(pathType=None, assetName=None, assetType=None, sceneName=None, episode=None):
    if pathType == 'asset':
        typeCode = assetType[0]
        if assetName.find('_') != -1: assetName = assetName[assetName.find('_')+1:]
        dataPath = ASSET_ROOT+'/'+PRJ_NAME+'/'+assetType+'/'+typeCode+'_'+assetName
    elif pathType == 'sequence':
        dataPath = SEQUENCE_ROOT+'/'+PRJ_NAME+'/EPISODES/'+str(episode)+'/'+str(sceneName)
    return dataPath

#Render-prep MCC========================================================================================================
def exportCamera(sceneDataPath=None):
    if sceneDataPath is None: raise registrarError, 'sceneDataPath not specified'
    if not cmds.objExists('cam'): raise registrarError, 'cam group non-exists'
    cmds.select('cam')
    if not os.path.isdir(sceneDataPath+'/camera'): os.makedirs(sceneDataPath+'/camera')
    cmds.file(sceneDataPath+'/camera/camera.ma', es=True, type='mayaAscii')
    return

def deleteExportedMcc(sceneDataPath=None, mccDirName=None):
    if sceneDataPath is None or mccDirName is None: raise registrarError, 'sceneDataPath not specified'
    shutil.rmtree(sceneDataPath+'/render/'+mccDirName)
    return

def listExportedMcc(sceneDataPath=None):
    if sceneDataPath is None: raise registrarError, 'sceneDataPath not specified'
    ret = []
    if not os.path.isdir(sceneDataPath+'/render'): os.makedirs(sceneDataPath+'/render')
    for item in os.listdir(sceneDataPath+'/render'):
        if os.path.isdir(sceneDataPath+'/render/'+item): ret.append(item)
    return ret

def renderVersionCheck(filePath=None):
    #filePath is the path to the specific asset file not including the name of the asset file tail.
    #This function will check if render version is available or not.
    if filePath is None: raise registrarError, 'datapath not specified'
    if filePath.find('/shader/') != -1: raise registrarError, 'unable to parse render file'

    #get assetName
    if filePath.find('{') != -1:
        filePath = filePath[:filePath.rfind('{')]
    assetName = filePath[filePath.rfind('/')+1:]
    dataPath = filePath[:filePath.rfind('/')]
    dataPath = dataPath[:dataPath.rfind('/')]

    ret = 0
    if os.path.isdir(dataPath+'/shader'):
        ret = 1
        if os.path.isfile(dataPath+'/shader/conData.xml'):
            ret = 1
            if os.path.isfile(dataPath+'/shader/'+assetName):
                ret = 1
            else:
                ret = 0
        else:
            ret = 0
    else:
        ret = 0
    return ret

def exportMcc(dataPath=None):
    #datapath is the asset path get from cmds.file(q=True, r=True)
    if dataPath is None: raise registrarError, 'datapath not specified'

    #get asset namespace and path
    assetNameSpace = cmds.referenceQuery(dataPath, ns=True).replace(':','')
    assetPath = dataPath[:dataPath.rfind('/')]
    assetPath = assetPath[:assetPath.rfind('/')]

    #get data from scene file
    sceneName = cmds.getAttr('sceneInfo.shotName', asString=True)
    episode = cmds.getAttr('sceneInfo.episodeName', asString=True)
    sequnceDataPath = genDataPath(pathType='sequence', sceneName=sceneName, episode=episode)
    frameCount = cmds.getAttr('sceneInfo.frameCount', asString=True)
    endTime = 100+int(frameCount)

    #select object based on conData.xml
    obj = []
    tree = ET.parse(assetPath+'/shader/conData.xml')
    root = tree.getroot()
    for chk in root:
        obj.append(assetNameSpace+':'+chk.text)
    cmds.select(obj)

    #export sceneInfo data
    if os.path.isfile(sequnceDataPath+'/info.xml'): os.remove(sequnceDataPath+'/info.xml')
    root = ET.Element('root')

    for attr in cmds.listAttr('sceneInfo', ud=True):
        tagWrite = ET.SubElement(root, attr)
        tagWrite.text = str(cmds.getAttr('sceneInfo.'+str(attr), asString=True))

    tree = ET.ElementTree(root)
    tree.write(sequnceDataPath+'/info.xml')

    #export mcc file to server
    if not os.path.isdir(sequnceDataPath+'/render/'+assetNameSpace): os.makedirs(sequnceDataPath+'/render/'+assetNameSpace)
    cmds.cacheFile(f=assetNameSpace, dir=sequnceDataPath+'/render/'+assetNameSpace, st=101, et=int(endTime), fm='OneFile', points=cmds.ls(sl=True))
    openVar = open(sequnceDataPath+'/render/'+assetNameSpace+'/filePath.txt', 'w')
    openVar.write(assetPath)
    openVar.close()
    return

def renderSceneBuilder(mccDataName=None, episodeName=None, sequenceName=None, includeCam=False):
    if mccDataName is None: raise registrarError, 'no mccData specified'
    if sequenceName is None: raise registrarError, 'no sequenceName specified'
    if episodeName is None: raise registrarError, 'no episodeName specified'

    sequenceDataPath = genDataPath(pathType='sequence', sceneName=sequenceName, episode=episodeName)
    readVar = open(sequenceDataPath+'/render/'+mccDataName+'/filePath.txt', 'r')
    readLine = readVar.readlines()
    readVar.close()

    assetType = mccDataName[0]

    assetRefPath = readLine
    assetRefPath = assetRefPath[0]

    #get assetName
    filePath = assetRefPath[:assetRefPath.rfind('{')] if assetRefPath.find('{') != -1 else assetRefPath
    assetName = filePath[filePath.rfind('/')+1:]
    dataPath = filePath[:filePath.rfind('/')]

    #rebuild shotMaster if not exists
    if not cmds.objExists('shotMaster'):
        cmds.group(em=True, n='shotMaster', world=True)
        cmds.group(em=True, n='sceneInfo', p='shotMaster')
        if not cmds.objExists('char'): cmds.group(em=True, n='char', p='shotMaster')
        if not cmds.objExists('prop'): cmds.group(em=True, n='prop', p='shotMaster')
        if not cmds.objExists('sets'): cmds.group(em=True, n='sets', p='shotMaster')

        #lock standard channel
        for object in ['shotMaster', 'sceneInfo', 'char', 'prop', 'sets']:
            for channel in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'visibility']:
                cmds.setAttr(object+'.'+channel, l=True, cb=False, k=False)

        tree = ET.parse(sequenceDataPath+'/info.xml')
        root = tree.getroot()
        cmds.select('sceneInfo')
        for item in root:
            cmds.addAttr(ln=str(item.tag),k=True,at='enum',en=str(item.text))
            cmds.setAttr('sceneInfo.'+str(item.tag),l=True)

        #re-build scene structure
        cmds.currentUnit(t=PRJ_UNIT)
        min = 101
        frameRange = int(cmds.getAttr('sceneInfo.frameCount', asString=True))
        max = 100+frameRange
        cmds.rangeControl('rangeControl1', e=True, min=min,\
                          max=max)

    #reference shaded model
    refAss = cmds.file(dataPath+'/'+assetName+'/shader/'+assetType+'_'+assetName+'.ma', r=True, namespace=mccDataName, f=True, mnc=False, gr=True)
    curimp = cmds.ls(sl=True)[0]
    if curimp.startswith('c_'):
        if not cmds.objExists('char'): cmds.group(em=True, n='char', p='shotMaster')
        cmds.parent(curimp, 'char')
    elif curimp.startswith('p_'):
        if not cmds.objExists('prop'): cmds.group(em=True, n='prop', p='shotMaster')
        cmds.parent(curimp, 'prop')
    elif curimp.startswith('s_'):
        if not cmds.objExists('sets'): cmds.group(em=True, n='sets', p='shotMaster')
        cmds.parent(curimp, 'sets')
    else:
        raise registrarError, 'invalid asset'

    #select object based on conData.xml
    obj = []
    tree = ET.parse(dataPath+'/'+assetName+'/shader/conData.xml')
    root = tree.getroot()
    for chk in root:
        obj.append(mccDataName+':'+chk.text)
    cmds.select(obj)

    #list mesh from selected
    meshObject = []
    for chk in cmds.ls(sl=True):
        meshObject.append(cmds.listHistory(chk, lf=True)[0])

    #reapply geo cache information
    xmlPath = SEQUENCE_ROOT+'/'+PRJ_NAME+'/EPISODES/'+episodeName+'/'+sequenceName+'/render/'+mccDataName+'/'+mccDataName+'.xml'
    pc.mel.doImportCacheFile(xmlPath, "", [meshObject], list())

    #include scene camera if available
    if includeCam is True:
        if not cmds.objExists('cam'):
            cmds.group(em=True, n='cam', p='shotMaster')
            cmds.file(sequenceDataPath+'/camera/camera.ma', r=True, namespace='cam', f=True, mnc=False, gr=True)
            curimp = cmds.ls(sl=True)[0]
            cmds.parent(curimp, 'cam')
    return
#Render-prep MCC========================================================================================================

#Asset Management Core==================================================================================================
#import asset to scene file
def importAsset(assetType=None,assetName=None):
    if assetType==None or assetName==None:
        cmds.confirmDialog(icn='warning',t='Error',message='No source specified', btn=['OK'])
        raise StandardError, 'error: no source specified'

    #check if temporer namespace exist
    for chk in cmds.ls():
        if chk.find('temporer')!=-1:
            try:
                cmds.delete(chk)
            except:
                pass

    path=ASSET_ROOT+'/'+assetType+'/'+assetName

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
        connectionVar=sqlite3.connect(SCRIPT_ROOT+'/ramDatabase.db')
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
        connectionVar=sqlite3.connect(SCRIPT_ROOT+'/ramDatabase.db')
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
        connectionVar=sqlite3.connect(SCRIPT_ROOT+'/ramDatabase.db')
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
        connectionVar=sqlite3.connect(SCRIPT_ROOT+'/ramDatabase.db')
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
    ramRecordLog(assetName=str(assetName),assetOperation='assetRegistration',user=CURRENT_USER,\
                 assetDescription='title:'+str(title)+',assetId:'+str(assetId))
    return

#List all log record from database
def listLogTable():
    #connect to database
    try:
        connectionVar=sqlite3.connect(SCRIPT_ROOT+'/ramDatabase.db')
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
        connectionVar=sqlite3.connect(SCRIPT_ROOT+'/ramDatabase.db')
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
        connectionVar=sqlite3.connect(SCRIPT_ROOT+'/ramDatabase.db')
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
    assetLocation=ASSET_ROOT+'/'+str(type)+'/'+str(name)

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
    ramRecordLog(assetName=str(name),assetOperation='assetRegistration',user=CURRENT_USER,\
                 assetDescription='assetName:'+str(name)+',assetType:'+str(type))
    return

#update asset record. This function will not affect maya file operation.
def updateAssetRecord(name=None,keyword=None,modelStat=None,shaderStat=None,rigStat=None,description=None):
    if name==None:raise StandardError, 'error : no name specified'

    #connect to database
    try:
        connectionVar=sqlite3.connect(SCRIPT_ROOT+'/ramDatabase.db')
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
    ramRecordLog(assetName=str(name),assetOperation='assetUpdateRecord',user=CURRENT_USER,\
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
    serverFileSavePathVar=str(ASSET_ROOT)+'/'+str(assetType)+'/'+str(name)+'/'+str(assetTarget)+'/'+str(prefixVar)+str(name)+'.ma'
    legacyFileSavePathVar=str(ASSET_ROOT)+'/'+str(assetType)+'/'+str(name)+'/_legacy/'+str(assetTarget)+'/'+str(prefixVar)+str(name)+timeStampVar+'.ma'
    textureSavePathVar=str(ASSET_ROOT)+'/'+str(assetType)+'/'+str(name)+'/texture'

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

    #additional to shader
    if assetTarget == 'shader':
        item = cmds.ls(type='mesh')
        root = ET.Element('root')
        for chk in item:
            tagWrite = ET.SubElement(root, chk)
            tagWrite.text = chk
        tree = ET.ElementTree(root)
        tree.write(str(ASSET_ROOT)+'/'+str(assetType)+'/'+str(name)+'/'+str(assetTarget)+'/conData.xml')

    #reopen local file
    cmds.file(localFileSavePathVar,o=True,f=True)

    #log record
    ramRecordLog(assetName=str(name),assetOperation='assetUpload',user=CURRENT_USER,\
                 assetDescription='assetName:'+str(name)+',assetType:'+str(assetType)+',assetTarget='+str(assetTarget))
    return

def downloadAsset(name=None, assetType=None, assetTarget=None):
    if name==None:raise StandardError, 'error : no asset name specified'
    if assetType==None or assetTarget==None: raise StandardError, 'error : no asset type or target specified'
    if assetTarget==None or assetTarget=='': raise StandardError, 'error : no asset target specified'

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
    serverFilePathVar=str(ASSET_ROOT)+'/'+str(assetType)+'/'+str(name)+'/'+str(assetTarget)+'/'+str(prefixVar)+str(name)+'.ma'
    serverFileDirVar=str(ASSET_ROOT)+'/'+str(assetType)+'/'+str(name)+'/'+str(assetTarget)
    legacyFileDirVar=str(ASSET_ROOT)+'/'+str(assetType)+'/'+str(name)+'/_legacy/'+str(assetTarget)

    #load procedure. copy file server to local then open the local version
    if os.path.isfile(serverFilePathVar)==False:
        raise StandardError, 'error : server file did not exists'
    shutil.copy(serverFilePathVar,localFilePathVar)
    cmds.file(localFilePathVar,o=True,f=True)

    #log record
    ramRecordLog(assetName=str(name),assetOperation='assetDownload',user=CURRENT_USER,\
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
    serverFilePathVar=str(ASSET_ROOT)+'/'+str(assetType)+'/'+str(assetName)+'/_legacy/'+str(assetTarget)+'/'+str(name)+'.ma'

    #open file
    shutil.copy(serverFilePathVar,localFilePathVar)
    cmds.file(localFilePathVar,o=True,f=True)

    #logger
    ramRecordLog(assetName=str(name),assetOperation='assetDownloadLegacy',user=CURRENT_USER,\
                 assetDescription='assetName:'+str(name)+',assetType:'+str(assetType)+',assetTarget='+str(assetTarget))

    return

def listAssetLegacyFiles(name=None):
    #connect to database
    try:
        connectionVar=sqlite3.connect(SCRIPT_ROOT+'/ramDatabase.db')
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
        connectionVar=sqlite3.connect(SCRIPT_ROOT+'/ramDatabase.db')
    except:
        raise StandardError,'error : failed to connect to database'

    connectionVar.execute("INSERT INTO ramAssetLog (logAssetName,logUser, logOperation, logDescription)"\
        "VALUES ('"+str(assetName)+"','"+str(user)+"','"+str(assetOperation)+"','"+str(assetDescription)+"')")
    connectionVar.commit()
    connectionVar.close()
    return
#Asset Management Core==================================================================================================

#Sequence Management Core===============================================================================================
def timestamp():
    date = datetime.datetime.now(); year = date.year;month = date.month; day = date.day
    hour = date.hour; minutes = date.minute; second = date.second
    return '['+str(year)+'-'+str(month)+'-'+str(day)+']('+str(hour)+','+str(minutes)+','+str(second)+')'

#playblast function
def playblasting(newTake=False):
    #fetch data from scene info
    project = cmds.getAttr('sceneInfo.projName', asString=True)
    episode = cmds.getAttr('sceneInfo.episodeName', asString=True)
    shot = cmds.getAttr('sceneInfo.shotName', asString=True)
    frameCount = int(cmds.getAttr('sceneInfo.frameCount', asString=True))

    #upload file normally
    uploadSeq()

    #validate cam existance
    if not cmds.objExists('cam'): raise StandardError, 'No cam group exists within scene file.'

    #generate general path
    genPath=SEQUENCE_ROOT+'/'+project+'/PLAYBLAST/'+episode

    #generate localTemp variable
    time = timestamp()
    localTemp = WIN_ROOT+'workspace/'+episode+'_'+shot+'_'+time+'.mov'

    #generating takeGen
    if newTake is False:
        takeGen = str(len(os.listdir(genPath)))
        if takeGen == '0':
            repVar = cmds.confirmDialog(icn='question', t='No Take',\
                                        m='There is no previous take. Would you like to add new take?',\
                                        button=['ADD TAKE', 'CANCEL'])
            takeGen = str(int(takeGen) + 1) if repVar != 'CANCEL' else None
    else:
        takeGen = str(len(os.listdir(genPath))+1)

    #playblasting
    if takeGen is not None:
        #impose frameCount
        cmds.playbackOptions(min=101, max=101+(int(frameCount)-1))

        winpbt=cmds.window('playblaster', t='Playblast', s=False)
        cmds.columnLayout(w=int(PLB_RESWIDTH), h=int(PLB_RESHEIGHT))
        cmds.paneLayout(w=int(PLB_RESWIDTH), h=int(PLB_RESHEIGHT))
        tmppnl=cmds.modelPanel(cam='shotCAM',mbv=False)

        cmds.modelEditor(cam='shotCAM', mp=tmppnl, dtx=True, j=False,\
                         ca=False, nc=False, pm=True, da='smoothShaded', lt=False)
        cmds.showWindow()
        cmds.setFocus(tmppnl)

        #playblasting
        pc.playblast(f=localTemp,\
                     fo=True,\
                     fmt=PLB_FORMAT,\
                     c=PLB_CODEC,\
                     p=80,\
                     qlt=100,\
                     uts=True,\
                     wh=[int(PLB_RESWIDTH)/1,int(PLB_RESHEIGHT)/1])
        cmds.deleteUI('playblaster', window=True)

        #playblast file operation
        if os.path.isdir(genPath+'/'+takeGen+'/playblast') == False:os.makedirs(genPath+'/'+takeGen+'/playblast')

        shutil.copy(localTemp, genPath+'/'+takeGen+'/playblast/'+episode+'_'+shot+'.mov')
        os.remove(localTemp)

        #save take file [continue from here]
        if not os.path.isdir(genPath+'/'+takeGen+'/file'):os.makedirs(genPath+'/'+takeGen+'/file')
        currentName = cmds.file(q=True, sn=True)
        shutil.copy(currentName, genPath+'/'+takeGen+'/file/'+episode+'_'+shot+'.ma')

        #open playblast file
        os.startfile(genPath+'/'+takeGen+'/playblast/'+episode+'_'+shot+'.mov')
    return

def viewPlayblast(eps=None, shot=None):
    shotPath = SEQUENCE_ROOT+'/'+PRJ_NAME+'/PLAYBLAST/'+eps
    for take in os.listdir(shotPath):take = take

    returnSearch = None
    while take !='0':
        if not os.path.isfile(shotPath+'/'+take+'/playblast/'+eps+'_'+shot+'.mov'):
            take = str(int(take)-1)
            returnSearch = True
        else:
            if returnSearch is not None:
                cmds.confirmDialog(icn='information', t='Previous take',\
                                   m='There is no latest take for this playblast. Playing take '+str(take)+'.',\
                                   button=['OK'])
            os.startfile(shotPath+'/'+take+'/playblast/'+eps+'_'+shot+'.mov')
            break
    return
#playblast function

#sequence uploading function
def uploadSeq():
    #check scene info
    if not cmds.objExists('sceneInfo'): raise StandardError, 'sceneInfo not found'

    #fetch data from scene info
    project = cmds.getAttr('sceneInfo.projName', asString=True)
    episode = cmds.getAttr('sceneInfo.episodeName', asString=True)
    shot = cmds.getAttr('sceneInfo.shotName', asString=True)

    #cross check scene and current project data
    if project != PRJ_NAME: raise StandardError, 'Invalid scene project data. Check your project environment.'

    #generating data path
    dataPath = SEQUENCE_ROOT+'/'+str(PRJ_NAME)+'/EPISODES/'+str(episode)+'/'+str(shot)

    #check data path existence
    if os.path.isdir(dataPath) is False:
        os.makedirs(dataPath)
        os.makedirs(dataPath+'/_legacy')

    #get current scene location
    curLoc = cmds.file(q=True, sn=True)
    #local save
    if curLoc == '':
        if os.path.isdir(WIN_ROOT+'workspace') is False: os.makedirs(WIN_ROOT+'workspace')
        curLoc = WIN_ROOT+'workspace/'+shot+'_'+str(timestamp())+'.ma'
        cmds.file(rename=curLoc)
        cmds.file(save=True, f=True, type='mayaAscii')
    else:
        cmds.file(save=True, f=True, type='mayaAscii')

    #backup file if it exists
    if os.path.isfile(dataPath+'/'+shot+'.ma'):
        shutil.copy(dataPath+'/'+shot+'.ma', dataPath+'/_legacy/'+shot+'_'+str(timestamp())+'.ma')

    #save file to server
    cmds.file(rename=dataPath+'/'+shot+'.ma')
    cmds.file(save=True, f=True, type='mayaAscii')

    #write log data
    logMan(dataPath=dataPath, string='File upload')

    #return file to local
    cmds.file(curLoc, o=True, f=True)
    return
#sequence uploading function

#sequence management function   
def listEps():
    return os.listdir(SEQUENCE_ROOT+'/'+PRJ_NAME+'/EPISODES')

def listShot(eps=None):
    if eps == None: raise StandardError, 'Incomplete credential submitted'
    return os.listdir(SEQUENCE_ROOT+'/'+PRJ_NAME+'/EPISODES/'+eps)

def getShotInformation(eps=None, shot=None):
    if eps == None or shot == None: raise StandardError, 'Incomplete credential submitted'

    #generate path
    path = SEQUENCE_ROOT+'/'+PRJ_NAME+'/EPISODES/'+eps+'/'+shot

    #get shotname
    shotName = None
    for item in os.listdir(path):
        if item.endswith('.ma') == True : shotName = item

    #get last handler
    tree = ET.parse(path+'/log.xml')
    root = tree.getroot()
    for chk in root:lastHandler = chk.get('user')

    #get number of version
    versionNum = len(os.listdir(path+'/_legacy'))
    return [shotName, lastHandler, versionNum]

def downloadSeq(eps=None, shot=None):
    if eps == None or shot == None: raise StandardError, 'Incomplete credential submitted'

    #generate path
    path = SEQUENCE_ROOT+'/'+PRJ_NAME+'/EPISODES/'+eps+'/'+shot

    #get seq file name
    shotName = None
    for item in os.listdir(path):
        if item.endswith('.ma'): shotName = item

    #copy file to local workspace
    if not os.path.isdir(WIN_ROOT+'/workspace'): os.makedirs(WIN_ROOT+'/workspace')
    time = timestamp()
    shutil.copy(path+'/'+shotName, WIN_ROOT+'/workspace/'+shotName[:shotName.rfind('.')]+'_'+time+'.ma')

    #open local file
    cmds.file(WIN_ROOT+'/workspace/'+shotName[:shotName.rfind('.')]+'_'+time+'.ma', o=True, f=True)

    #write log
    logMan(dataPath=path, string='File download')
    return
#sequence management function

#notes functions
def listNotes(eps=None, shot=None):
    if eps == None or shot == None: raise StandardError, 'Incomplete credential submitted'
    #generate path
    path = SEQUENCE_ROOT+'/'+PRJ_NAME+'/EPISODES/'+eps+'/'+shot

    #retrieve notes
    notesRet=None
    temp = []
    if os.path.isfile(path+'/notes.xml'):
        tree = ET.parse(path+'/notes.xml')
        root = tree.getroot()
        for item in root: temp.append([item.get('author'), item.get('time'), item.get('title'), item.text])
    return temp

def addNotes(eps=None, shot=None, title=None, notes=None):
    if eps == None or shot == None: raise StandardError, 'Incomplete credential submitted'
    #generate path
    path = SEQUENCE_ROOT+'/'+PRJ_NAME+'/EPISODES/'+eps+'/'+shot+'/notes.xml'

    if not os.path.isfile(path):
        root = ET.Element('root')
    else:
        tree = ET.parse(path)
        root = tree.getroot()

    #write log data
    log = ET.SubElement(root, 'notes')
    log.set('author', str(CURRENT_USER))
    log.set('time', str(timestamp()))
    log.set('title', title)
    log.text = str(notes)
    tree = ET.ElementTree(root)
    tree.write(path)
    return
#notes functions

#log function
def logMan(string=None, dataPath=None):
    if string is None or dataPath is None: raise StandardError, 'Incomplete credential submitted'

    #get tree root
    if not os.path.isfile(dataPath+'/log.xml'):
        root = ET.Element('root')
    else:
        tree = ET.parse(dataPath+'/log.xml')
        root = tree.getroot()

    #write log data
    log = ET.SubElement(root, 'log')
    log.set('user', str(CURRENT_USER))
    log.set('time', str(timestamp()))
    log.text = str(string)
    tree = ET.ElementTree(root)
    tree.write(dataPath+'/log.xml')
    return

def listLog(eps=None, shot=None):
    if eps == None or shot == None: raise StandardError, 'Incomplete credential submitted'
    #generate path
    path = SEQUENCE_ROOT+'/'+PRJ_NAME+'/EPISODES/'+eps+'/'+shot+'/log.xml'

    #get log list
    logList = []
    tree = ET.parse(path)
    root = tree.getroot()
    for chk in root:
        logList.append('time : '+str(chk.get('time'))+'\t'+'user : '+str(chk.get('user'))+'\t'+'operation : '+str(chk.text))
    return logList
#log function

#list legacy
def listLegacy(eps=None, shot=None):
    if eps == None or shot == None: raise StandardError, 'Incomplete credential submitted'

    #generate path
    path = SEQUENCE_ROOT+'/'+PRJ_NAME+'/EPISODES/'+eps+'/'+shot
    return os.listdir(path+'/_legacy')

def loadLegacy(eps=None, shot=None, file=None):
    if eps == None or shot == None or file == None: raise StandardError, 'Incomplete credential submitted'
    #generate path
    path = SEQUENCE_ROOT+'/'+PRJ_NAME+'/EPISODES/'+eps+'/'+shot

    #copy legacy to local workspace
    if not os.path.isdir(WIN_ROOT+'/workspace'): os.makedirs(WIN_ROOT+'/workspace')
    time = timestamp()
    shutil.copy(path+'/_legacy/'+file+'.ma', WIN_ROOT+'/workspace/'+shot+'_'+time+'.ma')

    #open local file
    cmds.file(WIN_ROOT+'/workspace/'+shot+'_'+time+'.ma',o=True, f=True)
    return
#list legacy

#Render-prep MCC
def mccPublishShader(assetName=None, assetType=None):
    #generate dataPath
    dataPath = genDataPath(pathType='asset', assetName=assetName, assetType=assetType)

    if os.path.isfile(dataPath+'/shader/conData.xml'): os.remove(dataPath+'/shader/conData.xml')
    return
#Render-prep MCC

#Sequence Management Core===============================================================================================