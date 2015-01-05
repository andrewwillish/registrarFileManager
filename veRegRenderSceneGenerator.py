__author__ = 'andrew.willis'

#import module
import maya.cmds as cmds
import asiist, veRegCore, os, getpass
import xml.etree.cElementTree as ET

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

#continue building the render script generator
class mncRegRenderSceneGenerator:
    def __init__(self):
        if cmds.window('renderSceneGenerator', exists=True): cmds.deleteUI('renderSceneGenerator', wnd=True)

        cmds.window('renderSceneGenerator', t='Render Scene Generator', s=False)
        cmas = cmds.columnLayout(adj=True)

        f1 = cmds.frameLayout(l='Scene Browse', w=200)
        cmds.columnLayout(adj=True)
        cmds.text(l='Episode Name:', al='left', fn='boldLabelFont', w=200)
        cmds.textScrollList('episodeName', w=200, h=80, sc=self.episodeChange)
        cmds.text(l='Sequence Name:', al='left', fn='boldLabelFont')
        cmds.textScrollList('sequenceName', w=200, h=80, en=False, sc=self.sequenceChange)

        f2 = cmds.frameLayout(l='Exported MCC Data', p=cmas)
        cmds.columnLayout(adj=True)
        cmds.textScrollList('serverMccData2',w=200, h=100, ams=True, en=False)

        f3 = cmds.frameLayout(l='Camera', p=cmas)
        cmds.columnLayout(adj=True)
        cmds.checkBox('includeCamera', l='Include Scene Camera', v=0)

        cmds.separator(p=cmas)
        cmds.button(l='GENERATE WITH ALL MCC', p=cmas, bgc=[1.0,0.643835616566,0.0], h=40,\
                    c=self.mccProcessAll)
        cmds.button(l='GENERATE WITH SELECTED MCC', p=cmas, c=self.mccProcessSingle)
        cmds.button(l='REFRESH', p=cmas, c=self.refresh)

        cmds.showWindow()

        #populate episode
        for item in os.listdir(SEQUENCE_ROOT+'/'+PRJ_NAME+'/EPISODES'):
            cmds.textScrollList('episodeName', e=True, a=item)
        return

    def mccProcessSingle(self, *args):
        episodeName = cmds.textScrollList('episodeName', q=True, si=True)
        sequenceName = cmds.textScrollList('sequenceName', q=True, si=True)
        mccData = cmds.textScrollList('serverMccData2', q=True, si=True)

        if mccData is None:
            cmds.confirmDialog(icn='warning', t='Error', m='Mcc Data is not selected.',\
                               button=['OK'])
            raise registrarError, 'no mcc data selected'
        mccData = mccData[0]

        if episodeName is not None and sequenceName is not None:
            episodeName = episodeName[0]
            sequenceName = sequenceName[0]
            if cmds.checkBox('includeCamera', q=True, v=True) is True:
                veRegCore.renderSceneBuilder(mccDataName=mccData,episodeName=episodeName, sequenceName=sequenceName, includeCam=True)
            else:
                veRegCore.renderSceneBuilder(mccDataName=mccData,episodeName=episodeName, sequenceName=sequenceName, includeCam=False)

        cmds.confirmDialog(icn='information', t='Done', m='Render scene generated.', button=['OK'])
        return

    def mccProcessAll(self, *args):
        episodeName = cmds.textScrollList('episodeName', q=True, si=True)
        sequenceName = cmds.textScrollList('sequenceName', q=True, si=True)

        if episodeName is not None and sequenceName is not None:
            episodeName = episodeName[0]
            sequenceName = sequenceName[0]
            for mccData in cmds.textScrollList('serverMccData2', q=True, ai=True):
                if cmds.checkBox('includeCamera', q=True, v=True) is True:
                    veRegCore.renderSceneBuilder(mccDataName=mccData,episodeName=episodeName, sequenceName=sequenceName, includeCam=True)
                else:
                    veRegCore.renderSceneBuilder(mccDataName=mccData,episodeName=episodeName, sequenceName=sequenceName, includeCam=False)
        cmds.confirmDialog(icn='information', t='Done', m='Render scene generated.', button=['OK'])
        return

    def sequenceChange(self, *args):
        episodeName = cmds.textScrollList('episodeName', q=True, si=True)
        sequenceName = cmds.textScrollList('sequenceName', q=True, si=True)
        if episodeName is not None and sequenceName is not None:
            episodeName = episodeName[0]
            sequenceName = sequenceName[0]
            sceneDataPath = veRegCore.genDataPath(pathType='sequence',\
                                                   sceneName=sequenceName,\
                                                   episode=episodeName)

            cmds.textScrollList('serverMccData2', e=True, ra=True, en=True)
            for item in os.listdir(sceneDataPath+'/render'):
                cmds.textScrollList('serverMccData2', e=True, a=item)
        else:
            cmds.textScrollList('serverMccData2', e=True, ra=True)
        return

    def episodeChange(self, *args):
        episodeName = cmds.textScrollList('episodeName', q=True, si=True)
        if episodeName is not None:
            episodeName = episodeName[0]
            cmds.textScrollList('sequenceName', e=True, ra=True, en=True)
            for item in os.listdir(SEQUENCE_ROOT+'/'+PRJ_NAME+'/EPISODES/'+episodeName):
                cmds.textScrollList('sequenceName', e=True, a=item)
        else:
            cmds.textScrollList('sequenceName', e=True, en=False)
        return

    def refresh(self, *args):
        import veRegRenderSceneGenerator
        reload (veRegRenderSceneGenerator)
        return

mncRegRenderSceneGenerator()