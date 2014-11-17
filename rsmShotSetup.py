__author__ = 'andrew.willis'

#Shot Setup - VE Version
#Andrew Willis 2014

import maya.cmds as cmds
import asiist

epsInts=[]
dataHeader=None

class shotSetupCls:
    def __init__(self):
        if cmds.window('veShotSetup',exists=True):cmds.deleteUI('veShotSetup',wnd=True)

        cmds.window('veShotSetup',t='Shot Setup', s=False)
        cmas=cmds.columnLayout(adj=True)

        f1=cmds.frameLayout(l='ECF File',p=cmas)
        cmds.rowColumnLayout(nc=2)
        cmds.textField('ecfBrowse',w=200)
        cmds.button(l='...',w=20,c=self.openFile)

        f3=cmds.frameLayout(l='Episode Name',p=cmas)
        cmds.text('episodeName',l='',h=30,fn='boldLabelFont')

        f2=cmds.frameLayout(l='Episode Content',p=cmas)
        cmds.columnLayout(adj=True)
        cmds.textScrollList('shotContent',w=220)
        cmds.showWindow()

        f4=cmds.frameLayout(l='Command',p=cmas)
        cmds.rowColumnLayout(nc=3)
        cmds.button(l='SETUP SHOT',c=lambda*args:self.setupShot(new=True),bgc=[1.0,0.643835616566,0.0])
        cmds.button(l='UPDATE SHOT',c=lambda*args:self.setupShot(new=False))
        cmds.button(l='CLEAR SHOT',c=self.deleteShot)
        return

    def deleteShot(self,*args):
        repVar=cmds.confirmDialog(icn='question',t='New',\
                                  m='This will clear current sequence. Proceed?',\
                                  button=['Ok','Cancel'])
        if repVar=='Ok':cmds.file(new=True,f=True)
        return

    def openFile(self,*args):
        global epsInts,dataHeader
        file=cmds.fileDialog()
        reader=open(file,'r')
        data=reader.readlines()
        reader.close()

        dataHeader=file[file.rfind('/')+1:]

        for chk in data:
            chk=chk.replace('\r\n','')
            epsInts.append([chk[:chk.find(':')],chk[chk.find(':')+1:]])

        cmds.textScrollList('shotContent',e=True,ra=True)
        for chk in epsInts:
            cmds.textScrollList('shotContent',e=True,a=chk[0])

        cmds.textField('ecfBrowse',e=True,tx=str(file))
        cmds.text('episodeName',e=True,l=file[file.rfind('/')+1:file.rfind('.')])
        return

    def setupShot(self,new=False):
        global epsInts,dataHeader
        if epsInts==[] or dataHeader==None:
            cmds.confirmDialog(icn='error',t='Error',m='No episode opened!',button=['OK'])
            cmds.error('error : no episode opened')

        selShot=cmds.textScrollList('shotContent',q=True,si=True)
        if selShot==None:
            cmds.confirmDialog(icn='error',t='Error',m='No shot selected!',button=['OK'])
            cmds.error('error : no shot selected')
        record=None
        for chk in epsInts:
            if chk[0]==selShot[0]:record=chk

        if new==True:
            if cmds.objExists('shotMaster'):
                cmds.confirmDialog(icn='error',t='Error',m='Shot master exists!',button=['OK'])
                cmds.error('error : shot master exists')
            cmds.group(em=True,n='shotMaster')
            self.sceneInfo()
            cmds.confirmDialog(icn='information',t='Done',m='Shot setup done.',button=['Ok'])
        else:
            if cmds.objExists('sceneInfo'):cmds.delete('sceneInfo')
            self.sceneInfo()
            cmds.confirmDialog(icn='information',t='Done',m='Shot update done.',button=['Ok'])
        return

    def sceneInfo(self):
        selShot=cmds.textScrollList('shotContent',q=True,si=True)
        record=None
        for chk in epsInts:
            if chk[0]==selShot[0]:record=chk

        #create empty group
        cmds.group(em=True,n='sceneInfo',p='shotMaster')
        cmds.group(em=True,n='char',p='shotMaster')
        cmds.group(em=True,n='prop',p='shotMaster')
        cmds.group(em=True,n='sets',p='shotMaster')
        cmds.group(em=True,n='cam',p='shotMaster')

        #additional data to sceneInfo
        cmds.select('sceneInfo')
        for chk in asiist.getEnvi():
            cmds.addAttr(ln=str(chk[0]),k=True,at='enum',en=str(chk[1]))
            cmds.setAttr('sceneInfo.'+str(chk[0]),l=True)
            if chk[0]=='unit':cmds.currentUnit(time=chk[1])

        cmds.addAttr(ln='__________',k=True,at='enum',en='__________')
        cmds.setAttr('sceneInfo.__________',l=True)
        cmds.addAttr(ln='episodeName',k=True,at='enum',en=str(cmds.text('episodeName',q=True,l=True)))
        cmds.setAttr('sceneInfo.episodeName',l=True)
        cmds.addAttr(ln='shotName',k=True,at='enum',en=str(record[0]))
        cmds.setAttr('sceneInfo.shotName',l=True)
        cmds.addAttr(ln='frameCount',k=True,at='enum',en=str(record[1]))
        cmds.setAttr('sceneInfo.frameCount',l=True)

        #lock standard channel
        for object in ['shotMaster','sceneInfo','char','prop','sets','cam']:
            for channel in ['tx','ty','tz','rx','ry','rz','sx','sy','sz','visibility']:
                cmds.setAttr(object+'.'+channel,l=True,cb=False,k=False)

        #impose shot range
        cmds.rangeControl(min=101,max=101+(int(record[1])-1))
        return

shotSetupCls()