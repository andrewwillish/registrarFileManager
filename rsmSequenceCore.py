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
import pymel.core as pm

#windows root
winRoot = os.environ['ProgramFiles'][:2]+'/'

#determin current user
currentUserVar = str(getpass.getuser())

#determining root path
rootPathVar = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#fetch data from projInfo
enviFetch=asiist.getEnvi()
for chk in enviFetch:
    if chk[0] == 'projName': curProj = chk[1]
    if chk[0] == 'resWidth': resWidth = chk[1]
    if chk[0] == 'resHeight': resHeight = chk[1]
    if chk[0] == 'playblastCodec': codec = chk[1]
    if chk[0] == 'playblastFormat': playblastFormat = chk[1]
#determine root location assetRootVar and sequenceRootVar
try:
    tree = ET.parse(rootPathVar+'/root.xml')
    root = tree.getroot()
    assetRootVar = root[0].text
    sequenceRootVar = root[1].text
except:
    raise StandardError, 'error : failed to fetch root.xml'

def timestamp():
    date = datetime.datetime.now(); year = date.year;month = date.month; day = date.day
    hour = date.hour; minutes = date.minute; second = date.second
    return '['+str(year)+'-'+str(month)+'-'+str(day)+']('+str(hour)+','+str(minutes)+','+str(second)+')'

#playblast function=================================================================================
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
    genPath=sequenceRootVar+'/'+project+'/PLAYBLAST/'+episode

    #generate localTemp variable
    time = timestamp()
    localTemp = winRoot+'workspace/'+episode+'_'+shot+'_'+time+'.mov'

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
        cmds.columnLayout(w=int(resWidth), h=int(resHeight))
        cmds.paneLayout(w=int(resWidth), h=int(resHeight))
        tmppnl=cmds.modelPanel(cam='shotCAM',mbv=False)

        cmds.modelEditor(cam='shotCAM', mp=tmppnl, dtx=True, j=False,\
                         ca=False, nc=False, pm=True, da='smoothShaded', lt=False)
        cmds.showWindow()
        cmds.setFocus(tmppnl)

        #playblasting
        pm.playblast(f=localTemp,\
                     fo=True,\
                     fmt=playblastFormat,\
                     c=codec,\
                     p=80,\
                     qlt=100,\
                     uts=True,\
                     wh=[int(resWidth)/1,int(resHeight)/1])
        cmds.deleteUI('playblaster', window=True)

        #playblast file operation
        if os.path.isdir(genPath+'/'+takeGen+'/playblast') == False:os.makedirs(genPath+'/'+takeGen+'/playblast')

        shutil.copy(localTemp, genPath+'/'+takeGen+'/playblast/'+episode+'_'+shot+'.mov')
        os.remove(localTemp)

        #save take file [continue from here]
        if os.path.isdir(genPath+'/'+takeGen+'/file') == False:os.makedirs(genPath+'/'+takeGen+'/file')
        currentName = cmds.file(q=True, sn=True)
        shutil.copy(currentName, genPath+'/'+takeGen+'/file/'+episode+'_'+shot+'.ma')

        #open playblast file
        os.startfile(genPath+'/'+takeGen+'/playblast/'+episode+'_'+shot+'.mov')
    return

def viewPlayblast(eps=None, shot=None):
    shotPath = sequenceRootVar+'/'+curProj+'/PLAYBLAST/'+eps
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
#playblast function=================================================================================

#sequence uploading function========================================================================
def uploadSeq():
    #check scene info
    if not cmds.objExists('sceneInfo'): raise StandardError, 'sceneInfo not found'

    #fetch data from scene info
    project = cmds.getAttr('sceneInfo.projName', asString=True)
    episode = cmds.getAttr('sceneInfo.episodeName', asString=True)
    shot = cmds.getAttr('sceneInfo.shotName', asString=True)

    #cross check scene and current project data
    if project!=curProj: raise StandardError, 'Invalid scene project data. Check your project environment.'

    #generating data path
    dataPath = sequenceRootVar+'/'+str(curProj)+'/EPISODES/'+str(episode)+'/'+str(shot)

    #check data path existence
    if os.path.isdir(dataPath) is False:
        os.makedirs(dataPath)
        os.makedirs(dataPath+'/_legacy')

    #get current scene location
    curLoc = cmds.file(q=True, sn=True)
    #local save
    if curLoc == '':
        if os.path.isdir(winRoot+'workspace') is False: os.makedirs(winRoot+'workspace')
        curLoc = winRoot+'workspace/'+shot+'_'+str(timestamp())+'.ma'
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
#sequence uploading function========================================================================

#sequence management function=======================================================================
def listEps():
    return os.listdir(sequenceRootVar+'/'+curProj+'/EPISODES')

def listShot(eps=None):
    if eps == None: raise StandardError, 'Incomplete credential submitted'
    return os.listdir(sequenceRootVar+'/'+curProj+'/EPISODES/'+eps)

def getShotInformation(eps=None, shot=None):
    if eps == None or shot == None: raise StandardError, 'Incomplete credential submitted'

    #generate path
    path = sequenceRootVar+'/'+curProj+'/EPISODES/'+eps+'/'+shot

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
    path = sequenceRootVar+'/'+curProj+'/EPISODES/'+eps+'/'+shot

    #get seq file name
    shotName = None
    for item in os.listdir(path):
        if item.endswith('.ma'): shotName = item

    #copy file to local workspace
    if not os.path.isdir(winRoot+'/workspace'): os.makedirs(winRoot+'/workspace')
    time = timestamp()
    shutil.copy(path+'/'+shotName, winRoot+'/workspace/'+shotName[:shotName.rfind('.')]+'_'+time+'.ma')

    #open local file
    cmds.file(winRoot+'/workspace/'+shotName[:shotName.rfind('.')]+'_'+time+'.ma', o=True, f=True)

    #write log
    logMan(dataPath=path, string='File download')
    return
#sequence management function=======================================================================

#notes functions====================================================================================
def listNotes(eps=None, shot=None):
    if eps == None or shot == None: raise StandardError, 'Incomplete credential submitted'
    #generate path
    path = sequenceRootVar+'/'+curProj+'/EPISODES/'+eps+'/'+shot

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
    path = sequenceRootVar+'/'+curProj+'/EPISODES/'+eps+'/'+shot+'/notes.xml'

    if not os.path.isfile(path):
        root = ET.Element('root')
    else:
        tree = ET.parse(path)
        root = tree.getroot()

    #write log data
    log = ET.SubElement(root, 'notes')
    log.set('author', str(currentUserVar))
    log.set('time', str(timestamp()))
    log.set('title', title)
    log.text = str(notes)
    tree = ET.ElementTree(root)
    tree.write(path)
    return
#notes functions====================================================================================

#log function========================================================================================
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
    log.set('user', str(currentUserVar))
    log.set('time', str(timestamp()))
    log.text = str(string)
    tree = ET.ElementTree(root)
    tree.write(dataPath+'/log.xml')
    return

def listLog(eps=None, shot=None):
    if eps == None or shot == None: raise StandardError, 'Incomplete credential submitted'
    #generate path
    path = sequenceRootVar+'/'+curProj+'/EPISODES/'+eps+'/'+shot+'/log.xml'

    #get log list
    logList = []
    tree = ET.parse(path)
    root = tree.getroot()
    for chk in root:
        logList.append('time : '+str(chk.get('time'))+'\t'+'user : '+str(chk.get('user'))+'\t'+'operation : '+str(chk.text))
    return logList
#log function========================================================================================

#list legacy=========================================================================================
def listLegacy(eps=None, shot=None):
    if eps == None or shot == None: raise StandardError, 'Incomplete credential submitted'

    #generate path
    path = sequenceRootVar+'/'+curProj+'/EPISODES/'+eps+'/'+shot
    return os.listdir(path+'/_legacy')

def loadLegacy(eps=None, shot=None, file=None):
    if eps == None or shot == None or file == None: raise StandardError, 'Incomplete credential submitted'
    #generate path
    path = sequenceRootVar+'/'+curProj+'/EPISODES/'+eps+'/'+shot

    #copy legacy to local workspace
    if not os.path.isdir(winRoot+'/workspace'): os.makedirs(winRoot+'/workspace')
    time = timestamp()
    shutil.copy(path+'/_legacy/'+file+'.ma', winRoot+'/workspace/'+shot+'_'+time+'.ma')

    #open local file
    cmds.file(winRoot+'/workspace/'+shot+'_'+time+'.ma',o=True)
    return
#list legacy=========================================================================================

#Render-prep MCC========================================================================================================
def mccPublishShader(assetName=None, assetType=None):
    #generate dataPath
    dataPath = genDataPath(pathType='asset', assetName=assetName, assetType=assetType)

    if os.path.isfile(dataPath+'/shader/conData.xml'): os.remove(dataPath+'/shader/conData.xml')
    return
#Render-prep MCC========================================================================================================
