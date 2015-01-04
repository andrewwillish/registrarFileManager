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