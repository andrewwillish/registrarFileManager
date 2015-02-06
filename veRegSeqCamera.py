#rsCameraGen
#Andrew Willis 2014

#import module
try:
    import maya.cmds as cmds
except:
    pass

#Preliminary Scene Data
try:
    episode=cmds.getAttr('sceneInfo.episodeName',asString=True)
    shot=cmds.getAttr('sceneInfo.shotName',asString=True)
    frameCount=cmds.getAttr('sceneInfo.frameCount',asString=True)
except:
    cmds.confirmDialog( icon='warning',title='Message', message='No shotMaster within the maya scene!', button=['Ok'] ,defaultButton='Ok' )
    cmds.error('No shot master within the scene')

class rsmCamRigCls:
    def __init__(self):
        if cmds.window('rsmCamrig', exists=True):
            cmds.deleteUI('rsmCamrig', window=True)

        cmds.window('rsmCamrig',t='Camera Rig',s=False,w=200)
        cmas=cmds.columnLayout(adj=True)

        f0=cmds.frameLayout(l='Primary Camera Creator',w=200,p=cmas)
        cmds.button(l='CREATE',bgc=[1.0,0.643835616566,0.0],h=30,c=self.createCamera)

        f3=cmds.frameLayout(l='Primary Camera Synoptic',w=200,p=cmas)
        cmds.columnLayout(adj=True)
        cmds.button(l='SELECT POS',c=lambda*args:self.selectPosition(1))
        cmds.button(l='SELECT TILT',c=lambda*args:self.selectPosition(2))
        cmds.button(l='SELECT SETTING',c=lambda*args:self.selectPosition(3))
        cmds.button(l='DELETE',bgc=[1,0,0],c=self.deleteCamera)
        cmds.showWindow()
        return

    def deleteCamera(self, *args):
        try:
            cmds.delete('cam')
            if cmds.objExists('cameraex'):
                cmds.delete('cameraex')
            if cmds.objExists('cameraex2'):
                cmds.delete('cameraex2')
        except:
            cmds.confirmDialog(icn='warning', title='Error', message='There is no cam group in scene file', \
                               button=['Ok'])
            cmds.error('error: there is no cam in scene file')
        return

    def selectPosition(self, mode):
        try:
            if mode==1:
                cmds.select('CAMPOS')
            elif mode==2:
                cmds.select('CAMTILT')
            else:
                cmds.select('CAMSET')
        except:
            cmds.confirmDialog(icn='warning', title='Error', message='There is no cam group in scene file', \
                               button=['Ok'])
            cmds.error('error: there is no cam in scene file')
        return

    def lockStandard(self, object):
        cmds.setAttr(object+'.translateX',k=False,l=True)
        cmds.setAttr(object+'.translateY',k=False,l=True)
        cmds.setAttr(object+'.translateZ',k=False,l=True)
        cmds.setAttr(object+'.rotateX',k=False,l=True)
        cmds.setAttr(object+'.rotateY',k=False,l=True)
        cmds.setAttr(object+'.rotateZ',k=False,l=True)
        cmds.setAttr(object+'.scaleX',k=False,l=True)
        cmds.setAttr(object+'.scaleY',k=False,l=True)
        cmds.setAttr(object+'.scaleZ',k=False,l=True)
        return

    def createCamera(self, *args):
        if not cmds.objExists('shotMaster'):
            cmds.confirmDialog( icon='warning',title='Message', message='No Shot master within the file!',\
                                button=['Ok'] ,defaultButton='Ok' )
            cmds.error('error: no shot master within the scene')

        if cmds.objExists('cam'):
            cmds.confirmDialog( icon='warning',title='Error', message='There is already a camera master in scene \
            file.', button=['Ok'] ,defaultButton='Ok' )
            cmds.error('error: no shot master within the scene')

        #CREATE CAMERA==============================================================================================
        shotCamera=cmds.camera(dfg=False,dr=True,ncp=1,dsa=True,dst=False,ff='horizontal',hfa=1.68,vfa=0.945,fs=5.6,\
                              fl=50,sa=144)
        shotCamera=shotCamera[0]
        cmds.rename(shotCamera,'shotCAM')
        #CREATE CAMERA==============================================================================================

        self.lockStandard('shotCAM')
        cmds.setAttr('shotCAM./visibility',l=True)
        cmds.group(n='CAMGRP', em=True)
        self.lockStandard('CAMGRP')
        cmds.setAttr('CAMGRP.visibility',k=False,l=True)
        cmds.group('CAMGRP',n='CAMTILT')
        cmds.setAttr('CAMTILT.scaleX',k=False,l=True)
        cmds.setAttr('CAMTILT.scaleY',k=False,l=True)
        cmds.setAttr('CAMTILT.scaleZ',k=False,l=True)
        cmds.setAttr('CAMTILT.visibility',k=False,l=True)
        cmds.group('CAMTILT',n='CAMPOS')
        cmds.setAttr('CAMPOS.scaleX',k=False,l=True)
        cmds.setAttr('CAMPOS.scaleY',k=False,l=True)
        cmds.setAttr('CAMPOS.scaleZ',k=False,l=True)
        cmds.setAttr('CAMPOS.visibility',k=False,l=True)
        cmds.group('CAMPOS',n='cam')
        self.lockStandard('cam')

        prjCode = cmds.getAttr('sceneInfo.projCode', asString=True)
        episode = cmds.getAttr('sceneInfo.episodeName', asString=True)
        shot = cmds.getAttr('sceneInfo.shotName', asString=True)
        cmds.annotate('shotCAM', p=(0.800, 0.511, -2.514))
        cmds.setAttr('annotationShape1.overrideEnabled',1)
        cmds.setAttr('annotationShape1.overrideColor',7)
        cmds.setAttr('annotationShape1.displayArrow', 0, l=True)
        cmds.setAttr('annotationShape1.overrideEnabled',1)
        cmds.setAttr('annotationShape1.overrideColor',7)
        cmds.rename('annotation1','anShotInformation')
        cmds.expression(n='cameraex2',o='anShotInformation',s='setAttr -type\
         "string" "anShotInformation.text" ("Scene: "+"'+prjCode+'_'+episode+'_'+shot+'");')
        cmds.parent('anShotInformation', 'CAMGRP')

        #CAM SETTING================================================================================================
        cmds.group(em=True,n='CAMSET')
        cmds.parent('CAMSET','CAMGRP')

        cmds.setAttr('CAMSET.translateX',k=False,l=True)
        cmds.setAttr('CAMSET.translateY',k=False,l=True)
        cmds.setAttr('CAMSET.translateZ',k=False,l=True)
        cmds.setAttr('CAMSET.rotateX',k=False,l=True)
        cmds.setAttr('CAMSET.rotateY',k=False,l=True)
        cmds.setAttr('CAMSET.rotateZ',k=False,l=True)
        cmds.setAttr('CAMSET.scaleX',k=False,l=True)
        cmds.setAttr('CAMSET.scaleY',k=False,l=True)
        cmds.setAttr('CAMSET.scaleZ',k=False,l=True)
        cmds.setAttr('CAMSET.visibility',k=False,l=True)

        #Custom Attribute
        cmds.addAttr( 'CAMSET',ln='FOV_alg_35', defaultValue=35,k=True )
        cmds.addAttr( 'CAMSET',ln='Far_Clip', defaultValue=100000.0,k=True )
        cmds.addAttr( 'CAMSET',ln='Near_Clip', defaultValue=1.0,k=True )

        #Connection
        cmds.connectAttr('CAMSET.FOV_alg_35','shotCAMShape.focalLength')
        cmds.setAttr('CAMSET.FOV_alg_35',50)

        MULTIDIVvar=cmds.createNode('multiplyDivide',n='cammultiply')
        cmds.setAttr(MULTIDIVvar+'.operation',2)
        cmds.setAttr(MULTIDIVvar+'.input2X',50)
        cmds.connectAttr('CAMSET.FOV_alg_35',MULTIDIVvar+'.input1X')
        #CAM SETTING================================================================================================

        #CELAN-UP===================================================================================================
        cmds.move(0,0,0,'CAMPOS.scalePivot')
        cmds.move(0,0,0,'CAMPOS.rotatePivot')

        cmds.move(0,0,0,'CAMTILT.scalePivot')
        cmds.move(0,0,0,'CAMTILT.rotatePivot')

        cmds.setAttr('shotCAM.translateX',e=True,l=True,k=False)
        cmds.setAttr('shotCAM.translateY',e=True,l=True,k=False)
        cmds.setAttr('shotCAM.translateZ',e=True,l=True,k=False)
        cmds.setAttr('shotCAM.rotateX',e=True,l=True,k=False)
        cmds.setAttr('shotCAM.rotateY',e=True,l=True,k=False)
        cmds.setAttr('shotCAM.rotateZ',e=True,l=True,k=False)
        cmds.setAttr('shotCAM.scaleX',e=True,l=True,k=False)
        cmds.setAttr('shotCAM.scaleY',e=True,l=True,k=False)
        cmds.setAttr('shotCAM.scaleZ',e=True,l=True,k=False)
        cmds.setAttr('shotCAM.visibility',e=True,l=True,k=False)

        cmds.parent('shotCAM', 'CAMGRP')
        #CELAN-UP===================================================================================================

        #Parenting
        cmds.parent('cam','shotMaster')

        cmds.select(cl=True)
        return

rsmCamRigCls()