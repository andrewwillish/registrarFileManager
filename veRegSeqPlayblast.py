__author__ = 'andrew.willis'

import os, shutil
try:
    import maya.cmds as cmds
except:
    pass
import xml.etree.cElementTree as ET
import asiist, datetime, getpass, veRegCore

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
        if cmds.window('rsmPlayblast', exists=True): cmds.deleteUI('rsmPlayblast', wnd=True)
        cmds.window('rsmPlayblast', t='Playblast', s=False)
        cmas = cmds.columnLayout(adj=True, w=200)

        f1 = cmds.frameLayout(l='Sequence Information', p=cmas)
        cmds.columnLayout(adj=True)
        cmds.rowColumnLayout(nc=2, cw=[(1, 70), (2, 130)])
        cmds.text(l='Project : ', al='left', fn='boldLabelFont')
        cmds.textField('prjInfo')
        cmds.text(l='Episodes : ', al='left', fn='boldLabelFont')
        cmds.textField('epsInfo')
        cmds.text(l='Shots : ', al='left', fn='boldLabelFont')
        cmds.textField('shtInfo')
        cmds.text(l='Total Take : ', al='left', fn='boldLabelFont')
        cmds.textField('crtTakeInfo')

        f2 = cmds.frameLayout(l='Take Information', p=cmas)
        cmds.columnLayout(adj=True)
        cmds.text('maStatus', l='N/A', bgc=[1, 1, 1])
        cmds.separator()
        cmds.textScrollList('takeScrollList', w=200, sc=self.takeInfoClick)

        cmds.separator(p=cmas)
        cmds.checkBox('newTakeCheck', v=True, l='Playblast as New Take', p=cmas, cc=self.checkBoxClick)
        cmds.separator(p=cmas)
        cmds.button(l='PLAYBLAST', p=cmas, c=self.playblastProc, h=40,bgc=[1.0,0.643835616566,0.0])
        cmds.button(l='REFRESH', c=self.refresh, p=cmas)

        cmds.showWindow()

        #fetch data from scene info
        project = cmds.getAttr('sceneInfo.projName', asString=True)
        episode = cmds.getAttr('sceneInfo.episodeName', asString=True)
        shot = cmds.getAttr('sceneInfo.shotName', asString=True)
        frameCount = int(cmds.getAttr('sceneInfo.frameCount', asString=True))

        #populate project
        cmds.textField('prjInfo', e=True, tx= project)
        cmds.textField('epsInfo', e=True, tx=episode)
        cmds.textField('shtInfo', e=True, tx=shot)
        cmds.textField('crtTakeInfo', e=True, tx=str(veRegCore.takeCheck()))

        itemLis = []
        cmds.textScrollList('takeScrollList', e=True, ra=True)
        for chk in os.listdir(sequenceRootVar+'/'+curProj+'/PLAYBLAST/'+episode+'/playblast'):
            if chk.endswith('.mov'):
                cmds.textScrollList('takeScrollList', e=True, a=chk.replace('.mov', ''))

        #create playblast directory
        if not os.path.isdir(sequenceRootVar+'/'+curProj+'/PLAYBLAST/'+episode):
            os.makedirs(sequenceRootVar+'/'+curProj+'/PLAYBLAST/'+episode)
        if not os.path.isdir(sequenceRootVar+'/'+curProj+'/PLAYBLAST/'+episode+'/file'):
            os.makedirs(sequenceRootVar+'/'+curProj+'/PLAYBLAST/'+episode+'/file')
        if not os.path.isdir(sequenceRootVar+'/'+curProj+'/PLAYBLAST/'+episode+'/playblast'):
            os.makedirs(sequenceRootVar+'/'+curProj+'/PLAYBLAST/'+episode+'/playblast')
        return

    def refresh(self, *args):
        import veRegSeqPlayblast
        reload (veRegSeqPlayblast)
        return

    def checkBoxClick(self, *args):
        if cmds.checkBox('newTakeCheck', q=True, v=True):
            cmds.textScrollList('takeScrollList', e=True, da=True)
            cmds.text('maStatus', e=True, l='N/A', bgc=[1, 1, 1])
        return

    def takeInfoClick(self):
        #fetch data from scene info
        project = cmds.getAttr('sceneInfo.projName', asString=True)
        episode = cmds.getAttr('sceneInfo.episodeName', asString=True)
        shot = cmds.getAttr('sceneInfo.shotName', asString=True)
        frameCount = int(cmds.getAttr('sceneInfo.frameCount', asString=True))

        cmds.checkBox('newTakeCheck', e=True, v=False)
        selItem = cmds.textScrollList('takeScrollList', q=True, si=True)
        if selItem != []:
            selItem = selItem[0]
            if os.path.isfile(sequenceRootVar+'/'+curProj+'/PLAYBLAST/'+episode+'/file/'+selItem+'.ma'):
                cmds.text('maStatus', e=True, l='MA FILE EXISTS', bgc=[0, 1, 0])
            else:
                cmds.text('maStatus', e=True, l='MA FILE NON EXISTS', bgc=[1, 0, 0])
        return

    def playblastProc(self, *args):
        if cmds.checkBox('newTakeCheck', q=True, v=True):
            repVar = cmds.confirmDialog(icn='information', t='Playblast [NEW TAKE]',\
                                        m='This will playblast current scene as the next take. Procees?',\
                               button=['YES', 'NO'])
            if repVar == 'YES': veRegCore.playblasting(newTake=True)
        else:
            repVar = cmds.confirmDialog(icn='information', t='Playblast [OLD TAKE]',\
                                        m='This will playblast current scene to the old take. Proceed?',\
                                        button=['YES', 'NO'])
            if repVar == 'YES':
                selItem = cmds.textScrollList('takeScrollList', q=True, si=True)
                if selItem != []:
                    selItem = selItem[0]
                    takeGen = selItem[selItem.rfind('_TK')+1:].replace('TK', '')
                    veRegCore.playblasting(newTake=False, takeGen=takeGen)
        self.refresh()
        return

rsmPlayblast()