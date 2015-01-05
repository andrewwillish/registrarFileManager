__author__ = 'andrew.willis'

#import module
import maya.cmds as cmds
import asiist, veRegCore, os

#cutom error declaration
class registrarError(Exception):
    def __init__(self, text):
        self.text = text
    def __str__(self):
        return repr(self.text)

#determining root path
SCRIPT_ROOT = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

if not cmds.objExists('shotMaster'):
    cmds.confirmDialog(icn='warning', t='Error', m='No shotMaster in scene file.', \
                       button=['OK'])
    raise registrarError, 'no shot master in scene file'

class mncRegRenderSceneManager:
    def __init__(self):
        if cmds.window('renderSceneMCCExport', exists=True): cmds.deleteUI('renderSceneMCCExport', wnd=True)

        cmds.window('renderSceneMCCExport', t='Render Scene Component Export', s=False)
        cmas = cmds.columnLayout(adj=True)

        f1 = cmds.frameLayout(l='Scene Information')
        cmds.columnLayout(adj=True)
        cmds.text(l='Episode Name:', al='left', fn='boldLabelFont', w=200)
        cmds.textField('episodeName', en=False)
        cmds.text(l='Sequence Name:', al='left', fn='boldLabelFont')
        cmds.textField('sequenceName', en=False)

        f3 = cmds.frameLayout(l='Exported MCC Data', p=cmas)
        cmds.columnLayout(adj=True)
        cmds.textScrollList('serverMccData', h=80)

        f2 = cmds.frameLayout(l='Current Scene Asset', p=cmas)
        cmds.columnLayout(adj=True)
        cf2 = cmds.rowColumnLayout(nc=2)
        cmds.columnLayout(adj=True, p=cf2)
        cmds.textScrollList('currentSceneData', w=150, h=176, sc=self.populateCurrentSceneAsset)

        cmds.columnLayout(adj=True, p=cf2)
        cmds.text(l='Namespace:', al='left', fn='boldLabelFont', w=200)
        cmds.textField('nameSpace', en=False)
        cmds.text(l='Source Path:', al='left', fn='boldLabelFont')
        cmds.textField('sourcePath', en=False)
        cmds.text(l='Render Version:', al='left', fn='boldLabelFont')
        cmds.text('renderVersion', l='')
        cmds.separator()
        cmds.button(l='EXPORT ALL AVAILABLE MCC', h=50, bgc=[1.0,0.643835616566,0.0], c=self.processAll)
        cmds.button(l='CLEAR ALL MCC', h=30, bgc=[1,0,0], c=self.deleteAllMcc)

        f3 = cmds.frameLayout(l='Scene Camera', p=cmas)
        cmds.columnLayout(adj=True)
        cmds.button(l='EXPORT SCENE CAMERA', c=self.expoCam)

        cmds.separator(p=cmas)
        cmds.button(l='REFRESH', p=cmas, c=self.refresh)
        cmds.showWindow()

        self.refresh()

        cmds.popupMenu(p='serverMccData')
        cmds.menuItem(l='Delete Exported MCC Data', c=self.deleteMcc)

        cmds.popupMenu(p='currentSceneData')
        cmds.menuItem(l='Export Selected MCC Data', c=self.processSingle)
        return


    def expoCam(self, *args):
        episodeName = cmds.getAttr('sceneInfo.episodeName', asString=True)
        seqName = cmds.getAttr('sceneInfo.shotName', asString=True)

        sceneDataPath = veRegCore.genDataPath(pathType='sequence', sceneName=seqName, episode=episodeName)
        veRegCore.exportCamera(sceneDataPath=sceneDataPath)

        cmds.confirmDialog(icn='information', t='Done', m='Camera successfully exported.', button=['OK'])
        return

    def deleteAllMcc(self, *args):
        #populate scene information
        episodeName = cmds.getAttr('sceneInfo.episodeName', asString=True)
        seqName = cmds.getAttr('sceneInfo.sequenceName', asString=True)
        cmds.textField('episodeName', e=True, tx=episodeName)
        cmds.textField('sequenceName', e=True, tx=seqName)
        dirLis = cmds.textScrollList('serverMccData', q=True, ai=True)

        #populate exported MCC data
        sceneDataPath = veRegCore.genDataPath(pathType='sequence', episode=episodeName, sceneName=seqName)

        repVar = cmds.confirmDialog(icn='question', t='Delete', m='Delete all MCC?',\
                                    button=['OK', 'CANCEL'])

        if repVar == 'OK':
            for dirName in dirLis:
                veRegCore.deleteExportedMcc(sceneDataPath=sceneDataPath, mccDirName=dirName)

        self.refresh()
        return

    def processAll(self, *args):
        #get file path
        for filePath in cmds.file(q=True, r=True):
            #check if render version is available
            if veRegCore.renderVersionCheck(filePath=filePath) == 0:
                cmds.confirmDialog(icn='warning', t='Error',\
                                   m='No render version available!', button='OK')
                cmds.error('render version is not available')
            veRegCore.exportMcc(dataPath=filePath)

        cmds.confirmDialog(icn='information', t='Done', m='MCC exported.', button=['OK'])
        self.refresh()
        return

    def processSingle(self, *args):
        #get file path
        refNode = cmds.textScrollList('currentSceneData', q=True, si=True)
        if refNode is not None:
            refNode = refNode[0]
        else:
            cmds.error('no mcc data selected')
        filePath = cmds.referenceQuery(refNode, f=True)

        #check if render version is available
        if veRegCore.renderVersionCheck(filePath=filePath) == 0:
            cmds.confirmDialog(icn='warning', t='Error',\
                               m='No render version available!', button='OK')
            cmds.error('render version is not available')

        veRegCore.exportMcc(dataPath=filePath)

        cmds.confirmDialog(icn='information', t='Done', m='MCC exported.', button=['OK'])
        self.refresh()
        return

    def refresh(self, *args):
        #clear field
        cmds.textField('nameSpace', e=True, tx='')
        cmds.textField('sourcePath', e=True, tx='')
        cmds.text('renderVersion', e=True, l='', nbg=True)

        #populate scene information
        episodeName = cmds.getAttr('sceneInfo.episodeName', asString=True)
        seqName = cmds.getAttr('sceneInfo.shotName', asString=True)
        cmds.textField('episodeName', e=True, tx=episodeName)
        cmds.textField('sequenceName', e=True, tx=seqName)

        #populate exported MCC data
        sceneDataPath = veRegCore.genDataPath(pathType='sequence', episode=episodeName, sceneName=seqName)
        mccLis = veRegCore.listExportedMcc(sceneDataPath=sceneDataPath)
        cmds.textScrollList('serverMccData', e=True, ra=True)
        for item in mccLis:
            cmds.textScrollList('serverMccData', e=True, a=item)

        #populate current scene asset
        cmds.textScrollList('currentSceneData', e=True, ra=True)
        for reffPath in cmds.file(q=True, r=True):
            namespace = cmds.referenceQuery(reffPath, rfn=True)
            cmds.textScrollList('currentSceneData', e=True, a=namespace)
        return

    def populateCurrentSceneAsset(self):
        selItem = cmds.textScrollList('currentSceneData', q=True, si=True)
        if selItem is None or len(selItem) > 1:
            cmds.confirmDialog(icn='warning', t='Error',\
                               m='No reference selected!', button='OK')
            cmds.error('no reference selected')

        selItem = selItem[0]
        filePath = cmds.referenceQuery(selItem, f=True)

        cmds.textField('nameSpace', e=True, tx=selItem)
        cmds.textField('sourcePath', e=True, tx=filePath)

        if veRegCore.renderVersionCheck(filePath=filePath) == 1:
            cmds.text('renderVersion', e=True, bgc=[0, 1, 0], l='AVAILABLE')
        else:
            cmds.text('renderVersion', e=True, bgc=[1, 0, 0], l='NOT AVAILABLE')
        return

    def deleteMcc(self, *args):
        #populate scene information
        episodeName = cmds.getAttr('sceneInfo.episodeName', asString=True)
        seqName = cmds.getAttr('sceneInfo.shotName', asString=True)
        cmds.textField('episodeName', e=True, tx=episodeName)
        cmds.textField('sequenceName', e=True, tx=seqName)
        dirName = cmds.textScrollList('serverMccData', q=True, si=True)
        if dirName is not None:
            dirName = dirName[0]
        else:
            cmds.error('no mcc data selected')

        #populate exported MCC data
        sceneDataPath = veRegCore.genDataPath(pathType='sequence', episode=episodeName, sceneName=seqName)

        repVar = cmds.confirmDialog(icn='question', t='Delete', m='Delete selected MCC?',\
                                    button=['OK', 'CANCEL'])
        if repVar == 'OK':
            veRegCore.deleteExportedMcc(sceneDataPath=sceneDataPath, mccDirName=dirName)

        self.refresh()
        return

mncRegRenderSceneManager()