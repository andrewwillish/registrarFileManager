__author__ = 'andrew.willis'

import os, shutil
try:
    import maya.cmds as cmds
except:
    pass
import xml.etree.cElementTree as ET
import asiist, datetime, getpass, rsmSequenceCore

#windows root
winRoot = os.environ['ProgramFiles'][:2]+'/'

#determine current project
enviFetch=asiist.getEnvi()
for chk in enviFetch:
    if chk[0] == 'projName': curProj=chk[1]

#determin current user
currentUserVar = str(getpass.getuser())

#determining root path
rootPathVar = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#determine root location assetRootVar and sequenceRootVar
try:
    tree = ET.parse(rootPathVar+'/root.xml')
    root = tree.getroot()
    assetRootVar = root[0].text
    sequenceRootVar = root[1].text
except:
    raise StandardError, 'error : failed to fetch root.xml'

class rsmPlayblast:
    def __init__(self):
        if not cmds.objExists('sceneInfo'):
            cmds.confirmDialog(icn='warning', t='Error',\
                               m='There is no sceneInfo in scene file.',\
                               button=['Ok'])
            raise StandardError, 'sceneInfo is not found'

        cmds.layoutDialog(ui=self.playblastUI, t='RSM Playblast')
        return

    def playblastUI(self):
        cmas = cmds.columnLayout(adj=True, w=200)
        cmds.text(l='Sequence Credential:', fn='boldLabelFont')
        cmds.text('seqCred', l='')
        cmds.text(l='',h=5)
        cmds.text(l='Current Shot Take:', fn='boldLabelFont')
        cmds.text('shotTake', l='')
        cmds.text(l='',h=5)
        cmds.text(l='Frame Count:', fn='boldLabelFont')
        cmds.text('frameCount', l='')
        cmds.text(l='',h=5)
        cmds.separator()
        cmds.rowColumnLayout(nc=2)
        cmds.button(l='PLAYBLAST', w=98, c=lambda*args:self.playblastProc(0), bgc=[1.0,0.643835616566,0.0])
        cmds.button(l='PLAYBLAST\nNEW TAKE', w=98, c=lambda*args:self.playblastProc(1))

        #fetch data from scene info
        project = cmds.getAttr('sceneInfo.projName', asString=True)
        episode = cmds.getAttr('sceneInfo.episodeName', asString=True)
        shot = cmds.getAttr('sceneInfo.shotName', asString=True)
        frameCount = int(cmds.getAttr('sceneInfo.frameCount', asString=True))

        #populating
        cmds.text('seqCred', e=True, l='EPS: '+episode+'\tSHT: '+shot)
        cmds.text('frameCount', e=True, l=str(frameCount)+' frames')

        if not os.path.isdir(sequenceRootVar+'/'+curProj+'/PLAYBLAST/'+episode):
            os.makedirs(sequenceRootVar+'/'+curProj+'/PLAYBLAST/'+episode)
        cmds.text('shotTake', e=True, l=str(len(os.listdir(sequenceRootVar+'/'+curProj+'/PLAYBLAST/'+episode))))
        return

    def playblastProc(self, mode):
        if mode == 0: cmds.layoutDialog(dismiss='PLAYBLAST')
        elif mode == 1: cmds.layoutDialog(dismiss='PLAYBLAST\nNEW TAKE')

        try:
            if mode == 0: rsmSequenceCore.playblasting(newTake=False)
            elif mode == 1: rsmSequenceCore.playblasting(newTake=True)
        except Exception as e:
            cmds.confirmDialog(icn='warning', \
                               t='Error',\
                               m=str(e),\
                               button=['OK'])
        return

rsmPlayblast()