__author__ = 'andrew.willis'

#import module
import maya.cmds as cmds
import os
import xml.etree.cElementTree as ET

#determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#determine root location assetRootVar and sequenceRootVar
try:
    tree=ET.parse(rootPathVar+'/root.xml')
    root=tree.getroot()
    assetRootVar=root[0].text
    assetRootVar=root[0].text
    sequenceRootVar=root[1].text
except Exception as e:
    print e
    raise StandardError, 'error : failed to fetch root.xml'

class assetImportUiClas:
    def __init__(self):
        if cmds.window('ramAssetImporter', exists=True): cmds.deleteUI('ramAssetImporter', wnd=True)

        cmds.window('ramAssetImporter',t='Asset Importer', s=False)
        cmas=cmds.columnLayout(adj=True)

        f1=cmds.frameLayout(l='Asset Search',p=cmas)
        cmds.columnLayout(adj=True)
        cmds.optionMenu('projectOptionMenu',w=200)

        f2=cmds.frameLayout(l='Asset Listing',p=cmas)
        cmds.textScrollList(w=200,h=200)

        f3=cmds.frameLayout(l='Asset Information',p=cmas)
        cmds.columnLayout(adj=True)
        cmds.text(l='picture',w=150,h=150)


        cmds.showWindow()
        return

    def refresh(self):
        self.populateTable()
        return

    def populateTable(self):
        #get all file list in server
        allCharLis=[];allPropsLis=[];allSetsLis=[]
        if os.path.isdir(assetRootVar+'/CHAR'):allCharLis=os.listdir(assetRootVar+'/CHAR')
        if os.path.isdir(assetRootVar+'/PROP'):allPropsLis=os.listdir(assetRootVar+'/PROP')
        if os.path.isdir(assetRootVar+'/SETS'):allSetsLis=os.listdir(assetRootVar+'/SETS')

        #get filter keyword
        charSearch=cmds.textField('charSearch',q=True,tx=True)
        propSearch=cmds.textField('propsSearch',q=True,tx=True)
        setSearch=cmds.textField('setsSearch',q=True,tx=True)

        #filtration process
        tempLis=[]
        if charSearch!='' and allCharLis!=[]:
            for chk in allCharLis: tempLis.append(chk) if chk.find(charSearch)!=-1 else None
            allCharLis=tempLis
        tempLis=[]
        if propSearch!='' and allPropsLis!=[]:
            for chk in allPropsLis: tempLis.append(chk) if chk.find(propSearch)!=-1 else None
            allPropsLis=tempLis
        tempLis=[]
        if setSearch!='' and allSetsLis!=[]:
            for chk in allSetsLis: tempLis.append(chk) if chk.find(setSearch)!=-1 else None
            allSetsLis=tempLis

        #populate table
        cmds.textScrollList('charTextScroll',e=True,ra=True)
        cmds.textScrollList('propsTextScroll',e=True,ra=True)
        cmds.textScrollList('setsTextScroll',e=True,ra=True)
        if allCharLis!=[]:
            for chk in allCharLis:cmds.textScrollList('charTextScroll',e=True,a=chk)
        if allPropsLis!=[]:
            for chk in allPropsLis:cmds.textScrollList('propsTextScroll',e=True,a=chk)
        if allSetsLis!=[]:
            for chk in allSetsLis:cmds.textScrollList('setsTextScroll',e=True,a=chk)
        return

    def importAsset(self,source=None):
        if source==None: cmds.confirmDialog(icn='warning',t='Error',message='No source specified', btn=['OK']);\
        raise StandardError, 'error: no source specified'

        #check if temporer namespace exist
        for chk in cmds.ls():
            if chk.find('temporer')!=-1:
                try:
                    cmds.delete(chk)
                except:
                    pass

        #determine path
        if source=='CHAR':
            asset=cmds.textScrollList('charTextScroll',q=True,si=True)[0]
        elif source=='PROP':
            asset=cmds.textScrollList('propsTextScroll',q=True,si=True)[0]
        elif source=='SETS':
            asset=cmds.textScrollList('setsTextScroll',q=True,si=True)[0]
        path=assetRootVar+'/'+source+'/'+asset

        #determine if there is any RENDER version or not
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

        #create standard group
        if cmds.objExists('all')==False:
            cmds.group(n='all',em=True)
            cmds.group(n='geo',em=True,p='all')
            cmds.group(n='rig',em=True,p='all')

        #file reference process
        #note: we reference the asset first to get the unique namespace implemented
        importPath=importPath+'/'+immediateFile

        if os.path.isfile(importPath)==True:
            reffFile= cmds.file(importPath,r=True,mnc=False,namespace=asset)

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
assetImportUiClas()