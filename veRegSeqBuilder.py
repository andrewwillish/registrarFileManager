__author__ = 'andrew.willis'

#Shot Setup - VE Version
#Andrew Willis 2014

import maya.cmds as cmds
import asiist, os
import xml.etree.cElementTree as ET
import veRegCore

#determining root path
rootPath=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

class shotBuilderCls:
    def __init__(self):
        if cmds.window('veShotBuilder',exists=True):cmds.deleteUI('veShotBuilder',wnd=True)

        cmds.window('veShotBuilder',t='Shot Builder',s=False)
        cmas=cmds.rowColumnLayout(nc=2)

        left=cmds.columnLayout(adj=True,p=cmas)
        f1=cmds.frameLayout(l='Asset Open',p=left)
        cmds.columnLayout(adj=True)
        cmds.optionMenu('assetType',w=150,cc=self.populate)
        cmds.menuItem(l='');cmds.menuItem(l='CHAR');cmds.menuItem(l='PROP');cmds.menuItem(l='SETS')
        cmds.text(l='Search Asset :',fn='boldLabelFont',al='left')
        cmds.textField('assetSearch',cc=self.populate)

        f2=cmds.frameLayout(l='Asset Content',p=left)
        cmds.columnLayout(adj=True)
        cmds.textScrollList('assetContent',w=150,h=150,sc=self.populateInformation)

        right=cmds.columnLayout(adj=True,p=cmas)
        f3=cmds.frameLayout(l='Asset Information',p=right)
        pf3=cmds.columnLayout(adj=True)
        f3split=cmds.rowColumnLayout(nc=2,p=pf3)
        cmds.columnLayout(adj=True,p=f3split)
        cmds.picture('preview',image=rootPath+'/NA.png',w=150,h=150)
        cmds.columnLayout(adj=True,p=f3split)
        cmds.text(l='Asset Name :',fn='boldLabelFont',al='left')
        cmds.textField('assetName',en=False)
        cmds.text(l='Asset Description :',fn='boldLabelFont',al='left')
        cmds.scrollField('assetDesc',h=70,en=False,ww=True)
        cmds.text(l='Asset Path :',fn='boldLabelFont',al='left')
        cmds.textField('assetPath',en=False)

        cmds.separator(p=pf3)
        cmds.button(l='REFERENCE ASSET TO CURRENT SCENE FILE',p=pf3,h=70,bgc=[1.0,0.730158729907,0.0],\
                    c=self.referenceAsset)

        cmds.showWindow()
        return

    def populateInformation(self,*args):
        #asset selection id
        assetId=cmds.textScrollList('assetContent',q=True,si=True)[0]
        assetId=assetId[:assetId.find('_')]
        for chk in veRegCore.listAssetTable():
            if str(chk[0])==assetId:
                assetName=chk[1]
                assetDesc=chk[8]
                assetPath=chk[4]

        #populating asset information
        cmds.textField('assetName',e=True,tx=assetName)
        cmds.scrollField('assetDesc',e=True,tx=assetDesc)
        cmds.textField('assetPath',e=True,tx=assetPath)

        #populate image
        if os.path.isfile(assetPath+'/preview.png')==True:
            cmds.picture('preview',e=True,image=assetPath+'/preview.png')
        else:
            cmds.picture('preview',e=True,image=rootPath+'/NA.png')
        return

    def populate(self,*args):
        #clear field
        cmds.picture('preview',e=True,image=rootPath+'/NA.png')
        cmds.textField('assetName',e=True,tx='')
        cmds.scrollField('assetDesc',e=True,tx='')
        cmds.textField('assetPath',e=True,tx='')

        #search string
        search=cmds.textField('assetSearch',q=True,tx=True)

        #asset type
        type=cmds.optionMenu('assetType',q=True,v=True)

        #populating asset content
        cmds.textScrollList('assetContent',e=True,ra=True)
        temp=[]
        write=[]
        for chk in veRegCore.listAssetTable():
            if chk[2]==type:write.append(chk)

        if search!='':
            for chk in write:
                if chk[1].find(search)!=-1:temp.append(chk)
            write=temp

        #populate textscroll
        cmds.textScrollList('assetContent',e=True,ra=True)
        for chk in write: cmds.textScrollList('assetContent',e=True,a=str(chk[0])+'_'+chk[1])
        return

    def referenceAsset(self,*args):
        if type==None: raise StandardError, 'error : no type specified'

        assetRefPath=cmds.textField('assetPath',q=True,tx=True)

        repVar=cmds.confirmDialog(icn='question',t='Select Sub-Type',m='Please select asset sub-type:',\
                                  button=['model','shader','rig','Cancel'])
        assetRefPath=assetRefPath+'/'+repVar

        fileName = None
        if repVar!='Cancel':
            if os.path.isdir(assetRefPath):
                for chk in os.listdir(assetRefPath):
                    if chk.endswith('.ma'): fileName = chk

                if fileName is not None:
                    refAss=cmds.file(assetRefPath+'/'+fileName,loadReferenceDepth='all',namespace=fileName.replace('.ma', ''),r=True,f=True,mnc=False,gr=True)
                    curimp=cmds.ls(sl=True)[0]
                    if curimp.startswith('c_'):
                        cmds.parent(curimp,'char')
                    elif curimp.startswith('p_'):
                        cmds.parent(curimp,'prop')
                    elif curimp.startswith('s_'):
                        cmds.parent(curimp,'sets')
                    else:
                        cmds.error('PROCEEDINGS ERROR: INVALID ASSET')
            else:
                cmds.confirmDialog(icn='warning',t='Error',message='Asset sub-type non-exists!\n'+assetRefPath,button=['OK'])
        return

shotBuilderCls()
