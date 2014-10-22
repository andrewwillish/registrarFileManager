__author__ = 'andrew.willis'

#Registrar Asset Manager - UI Module
#Andrew Willis 2014

#import module
import maya.cmds as cmds
import os, shutil
import ramAssetCore
import maya.OpenMaya as api
import maya.OpenMayaUI as apiUI
import xml.etree.cElementTree as ET
import getpass

#determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#determine root location assetRootVar and sequenceRootVar
try:
    tree=ET.parse(rootPathVar+'/root.xml')
    root=tree.getroot()
    assetRootVar=root[0].text
    sequenceRootVar=root[1].text
except:
    raise StandardError, 'error : failed to fetch root.xml'

#get current user
currentUserVar=str(getpass.getuser())

#ui class
class ramAssetUIClass:
    def __init__(self):
        #clear previous session window
        #ramAssetUI = This window, ramAssetTakePicture = preview taking window, ramAssetRegisterNew = register new asset record windows
        if cmds.window('ramAssetUI', exists=True):cmds.deleteUI('ramAssetUI', window=True)
        if cmds.window('ramAssetTakePicture', exists=True):cmds.deleteUI('ramAssetTakePicture', window=True)
        if cmds.window('ramAssetRegisterNew', exists=True):cmds.deleteUI('ramAssetRegisterNew', window=True)

        #main ui instruction
        cmds.window('ramAssetUI',t='RAM [Asset]',s=False,w=610)
        cmas=cmds.columnLayout(adj=True)
        cmds.rowColumnLayout('rowcmas',nc=2)

        cmds.frameLayout('f2',l='Asset Listing Table',p='rowcmas')
        cmds.columnLayout('cf2',adj=True)
        cmds.text(l='Asset Type : ',al='left',fn='boldLabelFont')
        cmds.optionMenu('assetTypeOption',cc=self.populateTable,w=150)
        cmds.menuItem(l='')
        cmds.menuItem(l='CHAR')
        cmds.menuItem(l='PROP')
        cmds.menuItem(l='SETS')
        cmds.text(l='Search Asset Name : ',al='left',fn='boldLabelFont')
        cmds.textField('assetSearchName',cc=self.populateTable,w=98)
        cmds.text(l='Search Asset Keywords : ',al='left',fn='boldLabelFont')
        cmds.textField('assetSearchKey',cc=self.populateTable,w=98)
        cmds.textScrollList('assetTextScroll',h=340,w=150,sc=self.listLegacyAndPicture)

        cmds.columnLayout('brdige',adj=True,p='rowcmas')
        cmds.frameLayout('f2inp',l='Asset Information',en=True)
        cmds.columnLayout('rrcf2',adj=True, p='f2inp')
        cmds.rowColumnLayout('rrcf22',nc=2, p='rrcf2')

        cmds.columnLayout('col1',adj=True,p='rrcf22')
        cmds.picture('screenshotPicture',h=150,w=150,i=rootPathVar+'/NA.png')

        cmds.columnLayout('col2',adj=True,p='rrcf22')
        cmds.text(l='Keywords : ',al='left',fn='boldLabelFont')
        cmds.text('assetInfoKey',al='left',l='')
        cmds.text(l='Description : ',al='left',fn='boldLabelFont')
        cmds.scrollField('assetDescription',wordWrap=True,tx='',h=55,en=False)
        cmds.text(l='Last Handler : ',al='left',fn='boldLabelFont')
        cmds.textField('assetLastHandler',en=False,tx='')
        cmds.columnLayout(adj=True)
        cmds.text(l='Asset Tracking : ',al='left',fn='boldLabelFont')
        cmds.rowColumnLayout(nc=3, cw=[(1,95),(2,95),(3,95)])
        cmds.checkBox('assetTrackModelCheck',l='Model',cc=lambda*args:self.changeAssetStatus('model'))
        cmds.checkBox('assetTrackShaderCheck',l='Shader',cc=lambda*args:self.changeAssetStatus('shader'))
        cmds.checkBox('assetTrackRigCheck',l='Rig',cc=lambda*args:self.changeAssetStatus('rig'))

        cmds.columnLayout( adj=True,p='rrcf2')
        cmds.separator()
        wVar=65
        cmds.rowColumnLayout(nc=7, cw=[(1,wVar),(2,wVar),(3,wVar),(4,wVar),(5,wVar),(6,wVar),(7,wVar)])
        cmds.button(l='REGISTER\nNEW',c=self.registerNewAssetUI,bgc=[1.0,0.730158729907,0.0])
        cmds.button(l='UPLOAD\nASSET',c=self.uploadAsset,bgc=[0.603174602805,1.0,0.0])
        cmds.button(l='DOWNLOAD\nASSET',c=self.downloadAsset,bgc=[0.0,1.0,1.0])
        cmds.button(l='VIEW\nLOG',c=self.viewLog)
        cmds.button(l='CHANGE\nKEYWORDS',c=self.changeKeywords)
        cmds.button(l='CHANGE\nDESC',c=self.changeDescription)
        cmds.button(l='IMPORT\nASSET',c=self.importAsset)

        cmds.frameLayout('f2inp2',l='Asset Notes', p='brdige',en=False)
        cmds.rowColumnLayout('f2inp2com',nc=2)
        cmds.columnLayout(adj=True,p='f2inp2com')
        cmds.text(l='Notes Listing : ',al='left',fn='boldLabelFont')
        cmds.textScrollList('notesList',w=150,sc=self.populateNotesField)
        cmds.columnLayout(adj=True,p='f2inp2com')
        cmds.text(l='Notes Title : ',al='left',fn='boldLabelFont',w=290)
        cmds.textField('notesTitleInfo',ed=False)
        cmds.text(l='Notes Author : ',al='left',fn='boldLabelFont',w=290)
        cmds.textField('notesAuthorInfo',ed=False)
        cmds.text(l='Notes Date : ',al='left',fn='boldLabelFont',w=290)
        cmds.textField('notesDateInfo',ed=False)
        cmds.separator()
        cmds.scrollField('notesMessageInfo',h=103,ed=False,wordWrap=True)

        cmds.frameLayout('f4',l='Asset Legacy Listing',p=cmas,en=False)
        cmds.columnLayout(adj=True)
        cmds.rowColumnLayout(nc=3)
        cmds.text(l='Model :', fn='boldLabelFont', al='left')
        cmds.text(l='Shader :', fn='boldLabelFont', al='left')
        cmds.text(l='Rig :', fn='boldLabelFont', al='left')
        cmds.textScrollList('legacyModelTextScroll',w=200)
        cmds.textScrollList('legacyShaderTextScroll',w=200)
        cmds.textScrollList('legacyRigTextScroll',w=200)
        cmds.showWindow()

        #popup menu for asset listing
        popperVar=cmds.popupMenu(p='assetInfoKey')
        cmds.menuItem(l='Change Keyword',c=self.changeKeywordFun)
        #popup menu for asset legacy listing
        popperVar2=cmds.popupMenu(p='legacyModelTextScroll')
        cmds.menuItem(l='Download Asset Legacy ', c=lambda*args: self.downloadLegacy(0))
        popperVar3=cmds.popupMenu(p='legacyShaderTextScroll')
        cmds.menuItem(l='Download Asset Legacy ', c=lambda*args: self.downloadLegacy(1))
        popperVar4=cmds.popupMenu(p='legacyRigTextScroll')
        cmds.menuItem(l='Download Asset Legacy ', c=lambda*args: self.downloadLegacy(2))
        #popup menu for picture
        popperVar5=cmds.popupMenu(p='screenshotPicture')
        cmds.menuItem(l='Take Asset Preview',p=popperVar5,c=lambda*args:cmds.layoutDialog(ui=self.takePicture))
        #popup menu for notes
        popperVar6=cmds.popupMenu(p='f2inp2')
        cmds.menuItem(l='Post New Notes',c=lambda*args:cmds.layoutDialog(t='New Notes',ui=self.postNotesUI))
        return

    def importAsset(self,*args):
        #get asset selection
        assetSelection=cmds.textScrollList('assetTextScroll',q=True,si=True)
        if assetSelection==None:
            cmds.confirmDialog(icn='warning',t='Error',message='No asset Selected',button=['OK'])
        else:
            assetSelection=assetSelection[0]

            #get asset type
            assetType=cmds.optionMenu('assetTypeOption',q=True,v=True)
            if assetType!='':
                ramAssetCore.importAsset(assetType=assetType, assetName=assetSelection)
        return

    def changeDescription(self,*args):
        assetSelection=cmds.textScrollList('assetTextScroll',q=True,si=True)
        if assetSelection==None:
            cmds.confirmDialog(icn='warning',t='Error',message='No asset Selected',button=['OK'])
        else:
            assetSelection=assetSelection[0]
            for chk in ramAssetCore.listAssetTable():
                if str(chk[1])==assetSelection:
                    repVar=cmds.promptDialog(t='Edit asset keywords',\
                        m='Please enter new asset description',\
                        tx=chk[8], button=['OK','CANCEL'])
                    if repVar=='OK':
                        newDesc=cmds.promptDialog(q=True,tx=True)
                        ramAssetCore.updateAssetRecord(name=assetSelection,\
                                                       description=newDesc)
            self.listLegacyAndPicture()
        return

    def changeKeywords(self,*args):
        assetSelection=cmds.textScrollList('assetTextScroll',q=True,si=True)
        if assetSelection==None:
            cmds.confirmDialog(icn='warning',t='Error',message='No asset Selected',button=['OK'])
        else:
            assetSelection=assetSelection[0]
            for chk in ramAssetCore.listAssetTable():
                if str(chk[1])==assetSelection:
                    repVar=cmds.promptDialog(t='Edit asset keywords',\
                        m='Please enter new asset keywords [separated by comma]',\
                        tx=chk[3], button=['OK','CANCEL'])
                    if repVar=='OK':
                        newDesc=cmds.promptDialog(q=True,tx=True)
                        ramAssetCore.updateAssetRecord(name=assetSelection,\
                                                       keyword=newDesc)
            self.listLegacyAndPicture()
        return

    def populateViewLog(self,*args):
        #get log id
        logSel=cmds.textScrollList('logTextScroll',q=True,si=True)
        logId=logSel[0][:logSel[0].find('_')]

        logNotes=None
        for chk in ramAssetCore.listLogTable():
            if str(chk[0])==logId:logNotes=chk

        if logNotes!=None:
            cmds.textField('idTextField',e=True,tx=logNotes[0])
            cmds.textField('userTextField',e=True,tx=logNotes[1])
            cmds.textField('dateTextField',e=True,tx=logNotes[5])
            cmds.textField('operationTextField',e=True,tx=logNotes[3])
            cmds.textField('descTextField',e=True,tx=logNotes[4])
        return

    def viewLog(self,*args):
        #validate asset selection
        assetSelection=cmds.textScrollList('assetTextScroll',q=True,si=True)
        if assetSelection==None:
            cmds.confirmDialog(icn='warning',t='Error',message='No asset Selected',button=['OK'])
        else:
            assetSelection=assetSelection[0]
            cmds.layoutDialog(ui=lambda*args:self.viewLogUI(assetSelection),t='Log View')
        return

    #list log
    def viewLogUI(self,assetSelection):
        #get log list
        logList=ramAssetCore.listLogTable()

        cmds.formLayout()
        cmas=cmds.columnLayout(adj=True)
        rcmas=cmds.rowColumnLayout(nc=2,cw=[(1,150),(2,300)])
        f1=cmds.frameLayout(l='Log Date',p=rcmas)
        cmds.textScrollList('logTextScroll',sc=self.populateViewLog)
        f2=cmds.frameLayout(l='Detail',p=rcmas)
        cmds.text(l='Id:',al='left',fn='boldLabelFont')
        cmds.textField('idTextField',en=False)
        cmds.text(l='User:',al='left',fn='boldLabelFont')
        cmds.textField('userTextField',en=False)
        cmds.text(l='Date:',al='left',fn='boldLabelFont')
        cmds.textField('dateTextField',en=False)
        cmds.text(l='Operation:',al='left',fn='boldLabelFont')
        cmds.textField('operationTextField',en=False)
        cmds.text(l='Detail:',al='left',fn='boldLabelFont')
        cmds.textField('descTextField',en=False)

        #populate log date
        cmds.textScrollList('logTextScroll',e=True,ra=True)
        for chk in logList:
            if chk[2]==assetSelection:cmds.textScrollList('logTextScroll',e=True,a=str(chk[0])+'_'+chk[5])
        return

    #populate notes field
    def populateNotesField(self,*args):
        #get notes date and assetId
        selNotesDateVar=cmds.textScrollList('notesList',q=True,si=True)
        if selNotesDateVar==None:
            raise StandardError, 'error : no notes selected'
        selNotesDateVar=selNotesDateVar[0]
        selAssetVar=cmds.textScrollList('assetTextScroll', q=True, si=True)
        if selAssetVar==None:
            raise StandardError, 'error : no asset selected'
        selAssetVar=selAssetVar[0]

        #find asset ID
        assetIdVar=''
        for chk in ramAssetCore.listAssetTable():
            if chk[1]==str(selAssetVar):
                assetIdVar=chk[0]
        if assetIdVar=='':
            cmds.confirmDialog(icn='warning', t='Error', m='Database anomaly no asset found.', button=['OK'])
            raise StandardError, 'error : database anomaly asset not found'

        for chk in ramAssetCore.listAssetNotes():
            if chk[4]==selNotesDateVar and str(assetIdVar) == str(chk[1]):
                cmds.textField('notesTitleInfo',e=True,tx=str(chk[2]))
                cmds.textField('notesAuthorInfo',e=True,tx=str(chk[3]))
                cmds.textField('notesDateInfo',e=True,tx=str(chk[4]))
                cmds.scrollField('notesMessageInfo',e=True,tx=str(chk[5]))
        return

    #change keyword
    def changeKeywordFun(self,*args):
        #get asset name from main textScrollList
        assetNameVar=cmds.textScrollList('assetTextScroll',q=True,si=True)
        if assetNameVar==None:
            cmds.confirmDialog(icn='warning', t='Error', m='No asset selected from asset list.', button=['Ok'])
            raise StandardError, 'error : no asset selected from asset list'
        assetNameVar=assetNameVar[0]

        #determin asset keyword based on assetName Var
        assetKeyVar=''
        for chk in ramAssetCore.listAssetTable():
            if chk[1]==str(assetNameVar):
                assetKeyVar=chk[3]
        if assetKeyVar=='':
            cmds.confirmDialog(icn='warning', t='Error', m='Cannot find record for '+str(assetNameVar)+'!',\
                               button=['Ok'])
            raise ValueError, 'error : database anomaly record non exists'

        repVar=cmds.promptDialog(t='Edit Asset Keyword',m='Enter new keyword',button=['OK','CANCEL'],tx=str(assetKeyVar))
        if repVar!='CANCEL':
            ramAssetCore.updateAssetRecord(name=str(assetNameVar),keyword=str(cmds.promptDialog(q=True,tx=True)))
        self.listLegacyAndPicture()
        return

    #preview taking process function
    def takePictureProcess(self, *args):
        global screenShotPanelVar
        #get asset name from main textScrollList
        assetNameVar=cmds.textScrollList('assetTextScroll',q=True,si=True)
        if assetNameVar==None:
            cmds.confirmDialog(icn='warning', t='Error', m='No asset selected from asset list.', button=['Ok'])
            raise StandardError, 'error : no asset selected from asset list'
        assetNameVar=assetNameVar[0]

        #determin asset type based on assetName Var
        assetTypeVar=''
        for chk in ramAssetCore.listAssetTable():
            if chk[1]==str(assetNameVar):
                assetTypeVar=chk[2]
        if assetTypeVar=='':
            cmds.confirmDialog(icn='warning', t='Error', m='Cannot find record for '+str(assetNameVar)+'!',\
                               button=['Ok'])
            raise ValueError, 'error : database anomaly record non exists'

        #image exporting instruction
        cmds.select(cl=True)
        cmds.setFocus(screenShotPanelVar)
        modelsPanelVar=apiUI.M3dView.active3dView()
        imageVar=api.MImage()
        modelsPanelVar.readColorBuffer(imageVar, True)
        imageVar.writeToFile(assetRootVar+'/'+assetTypeVar+'/'+assetNameVar+'/preview.png','png')

        #clear preview taking window
        cmds.layoutDialog(dismiss='SET AS PREVIEW')

        #refresh
        self.listLegacyAndPicture()
        return

    #preview taking UI function
    def takePicture(self,*args):
        global screenShotPanelVar
        cmds.formLayout()
        cmas=cmds.columnLayout(adj=True)
        cmds.paneLayout(w=150,h=150)
        screenShotPanelVar=cmds.modelPanel(cam='persp',mbv=False)
        cmds.modelEditor(screenShotPanelVar,e=True,da='smoothShaded',hud=False,jx=False,dtx=True,grid=False)
        cmds.separator(p=cmas)
        cmds.button(l='SET AS PREVIEW',p=cmas, c=self.takePictureProcess)
        return

    #this function download legacy asset
    #mode [0]=model, [1]=shader, [2]=rig
    def downloadLegacy(self,mode ):
        #get asset name from assetTextScrollList to determine the asset type later on
        assetNameSearchVar=cmds.textScrollList('assetTextScroll',q=True,si=True)
        if assetNameSearchVar==None:
            cmds.confirmDialog(icn='warning', t='Error', m='No asset selected from asset list.', button=['Ok'])
            raise StandardError, 'error : no asset selected from asset list'
        assetNameSearchVar=assetNameSearchVar[0]

        #get legacy asset file name from each of the legacy type scrollList
        assetNameVar=None
        if mode==0:
            assetNameVar=cmds.textScrollList('legacyModelTextScroll',q=True,si=True)
        elif mode==1:
            assetNameVar=cmds.textScrollList('legacyShaderTextScroll',q=True,si=True)
        elif mode==2:
            assetNameVar=cmds.textScrollList('legacyRigTextScroll',q=True,si=True)
        if assetNameVar==None:
            cmds.confirmDialog(icn='warning', t='Error', m='No asset selected from asset legacy list.', button=['Ok'])
            raise StandardError, 'error : no asset selected from asset legacy list'
        assetNameVar=assetNameVar[0].replace('.ma','')

        #determining asset type
        assetTypeVar=''
        for chk in ramAssetCore.listAssetTable():
            if chk[1]==str(assetNameSearchVar):
                assetTypeVar=chk[2]
        if assetTypeVar=='':
            cmds.confirmDialog(icn='warning', t='Error', m='Cannot find record for '+str(assetNameVar)+'!',\
                               button=['Ok'])
            raise ValueError, 'error : database anomaly record non exists'

        #confirm dialog to confirm proceeding
        repVar=cmds.confirmDialog(icn='question',t='Download',m='Download selected asset?',button=['Proceed','Cancel'])

        if repVar=='Proceed':
            #download instruction
            if mode==0:
                mode='model'
            elif mode==1:
                mode='shader'
            elif mode==2:
                mode='rig'

            if assetTypeVar=='CHAR':
                assetTypeVar=0
            elif assetTypeVar=='PROP':
                assetTypeVar=1
            elif assetTypeVar=='SETS':
                assetTypeVar=2

            try:
                ramAssetCore.downloadAssetLegacy(name=assetNameVar,assetType=assetTypeVar,assetTarget=mode)
            except Exception as e:
                cmds.confirmDialog(icn='warning', t='Error', m='File did not exists', button=['Ok'])
                raise StandardError, str(e)
        return

    #this function populate scrollList
    def populateTable(self,*args):
        #enable field
        cmds.frameLayout('f2inp2',e=True,en=False)
        cmds.frameLayout('f4',e=True,en=False)

        #clean up
        cmds.textScrollList('notesList',e=True,ra=True)
        cmds.textField('notesDateInfo',e=True,tx='')
        cmds.textField('notesTitleInfo',e=True,tx='')
        cmds.textField('notesAuthorInfo',e=True,tx='')
        cmds.scrollField('notesMessageInfo',e=True,tx='')
        cmds.scrollField('assetDescription',e=True,tx='')
        cmds.textField('assetLastHandler',e=True,tx='')

        #close residue of the previous session
        if cmds.window('ramAssetTakePicture', exists=True):cmds.deleteUI('ramAssetTakePicture', window=True)

        #set image preview and the rest of information field to default
        cmds.picture('screenshotPicture',e=True,image=rootPathVar+'/NA.png')
        cmds.checkBox('assetTrackModelCheck',e=True,v=False)
        cmds.checkBox('assetTrackShaderCheck',e=True,v=False)
        cmds.checkBox('assetTrackRigCheck',e=True,v=False)
        cmds.text('assetInfoKey',e=True,l='')

        #get asset type selection
        assetTypeSelection=cmds.optionMenu('assetTypeOption',q=True,v=True)

        #get all record from server
        allRecord=ramAssetCore.listAssetTable()

        #filter by record type
        writeLis=[]
        tempLis=[]
        for chk in allRecord:
            if chk[2]==assetTypeSelection:tempLis.append(chk)
        writeLis=tempLis
        tempLis=[]

        #filter by record name
        nameSearch=cmds.textField('assetSearchName',q=True,tx=True)
        if nameSearch!='':
            for chk in writeLis:
                if chk[1].find(str(nameSearch))!=-1:tempLis.append(chk)
            writeLis=tempLis
        tempLis=[]

        #filter by record keyword
        keySearch=cmds.textField('assetSearchKey',q=True,tx=True)
        if keySearch!='':
            keySearch=keySearch.replace(' ','')
            keySearch=keySearch.split(',')
            for chk in writeLis:
                keywordLis=chk[3].replace(' ','').split(',')
                valueVar=[i for i in keySearch if i in keywordLis]
                if valueVar!=[]:tempLis.append(chk)
            writeLis=tempLis
        tempLis=[]

        #populating information to field
        cmds.textScrollList('assetTextScroll',e=True,ra=True)
        cmds.textScrollList('legacyModelTextScroll',e=True,ra=True)
        cmds.textScrollList('legacyShaderTextScroll',e=True,ra=True)
        cmds.textScrollList('legacyRigTextScroll',e=True,ra=True)
        writeLis.sort()

        #sorting and populate based on alphabet
        tempLis=[]
        cnt=0
        for chk in writeLis:tempLis.append(chk[1].lower()+'_'+str(cnt));cnt+=1
        tempLis.sort()
        for chk in tempLis:
            indexNum=chk[chk.find('_')+1:]
            cmds.textScrollList('assetTextScroll',e=True,a=writeLis[int(indexNum)][1])
        return

    def postNotesUI(self,*args):
        cmds.formLayout(w=200)
        cmds.columnLayout(adj=True)
        cmds.text(l='Notes Title : ', al='left', fn='boldLabelFont',w=200)
        cmds.textField('newNotesTitle')
        cmds.text(l='Notes Message : ', al='left', fn='boldLabelFont',w=200)
        cmds.scrollField('newNotesMessage',w=200,ww=True,ed=True)
        cmds.separator()
        cmds.rowColumnLayout(nc=2)
        cmds.button(l='POST',w=100, c=lambda*args:self.postNotes(1))
        cmds.button(l='CANCEL',w=100, c=lambda*args:self.postNotes(0))
        return

    def postNotes(self,mode):
        if mode==0:
            cmds.layoutDialog(dismiss='CANCEL')
        else:
            cmds.layoutDialog(dismiss='POST')

            #get credential
            titleVar=cmds.textField('newNotesTitle',q=True,tx=True)
            authorVar=currentUserVar
            messageVar=cmds.scrollField('newNotesMessage',q=True,tx=True)

            #get asset name
            assetNameVar=cmds.textScrollList('assetTextScroll',q=True,si=True)
            if assetNameVar==None:
                cmds.confirmDialog(icn='warning', t='Error', m='No asset selected from asset list.', button=['Ok'])
                self.populateTable()
                raise StandardError, 'error : no asset selected from asset list'
            assetNameVar=assetNameVar[0]

            #get asset id
            assetIdVar=''
            for chk in ramAssetCore.listAssetTable():
                if chk[1]==assetNameVar:
                    assetIdVar=chk[0]
            if assetIdVar=='':
                cmds.confirmDialog(icn='warning',t='Error',m='Database anomaly! No asset named '+assetNameVar+' in database.',\
                                   button=['OK'])
                raise StandardError, 'error : database anomaly no asset found'

            try:
                ramAssetCore.postNewNotes(title=titleVar,author=authorVar,message=messageVar,\
                                          assetId=assetIdVar, assetName=assetNameVar)
            except Exception as e:
                cmds.confirmDialog(icn='warning', t='Error', m=str(e), button=['OK'])
                raise StandardError, str(e)
        self.listLegacyAndPicture()
        return

    #list legacy and preview picture
    def listLegacyAndPicture(self,*args):
        #enable field
        cmds.frameLayout('f2inp2',e=True,en=True)
        cmds.frameLayout('f4',e=True,en=True)

        #clean up
        cmds.textScrollList('notesList',e=True,ra=True)

        cmds.textField('notesTitleInfo',e=True,tx='')
        cmds.textField('notesAuthorInfo',e=True,tx='')
        cmds.textField('notesDateInfo',e=True,tx='')
        cmds.scrollField('notesMessageInfo',e=True,tx='')
        cmds.scrollField('assetDescription',e=True,tx='')
        cmds.textField('assetLastHandler',e=True,tx='')

        #close any residue from previous session window
        if cmds.window('ramAssetTakePicture', exists=True):cmds.deleteUI('ramAssetTakePicture', window=True)

        #get asset name
        assetNameVar=cmds.textScrollList('assetTextScroll',q=True,si=True)
        if assetNameVar==None:
            cmds.confirmDialog(icn='warning', t='Error', m='No asset selected from asset list.', button=['Ok'])
            raise StandardError, 'error : no asset selected from asset list'
        assetNameVar=assetNameVar[0]

        #populating model shader and rig legacy
        allLegacy= ramAssetCore.listAssetLegacyFiles(name=assetNameVar)

        cmds.textScrollList('legacyModelTextScroll',e=True,ra=True)
        for chk in allLegacy[0]:cmds.textScrollList('legacyModelTextScroll',e=True,a=str(chk))
        cmds.textScrollList('legacyShaderTextScroll',e=True,ra=True)
        for chk in allLegacy[1]:cmds.textScrollList('legacyShaderTextScroll',e=True,a=str(chk))
        cmds.textScrollList('legacyRigTextScroll',e=True,ra=True)
        for chk in allLegacy[2]:cmds.textScrollList('legacyRigTextScroll',e=True,a=str(chk))

        #clear notes listing table
        cmds.textScrollList('notesList',e=True,ra=True)

        #populating asset information
        allRecord=ramAssetCore.listAssetTable()
        for chk in allRecord:
            if chk[1]==assetNameVar:
                #populating keyword
                cmds.text('assetInfoKey',e=True,l=str(chk[3].replace(' ','')))

                #populating model checkbox
                if chk[5]=='0':
                    valVar=False
                elif chk[5]=='2':
                    valVar=True
                cmds.checkBox('assetTrackModelCheck',e=True,v=valVar)

                #populating shader checkbox
                if chk[6]=='0':
                    valVar=False
                elif chk[6]=='2':
                    valVar=True
                cmds.checkBox('assetTrackShaderCheck',e=True,v=valVar)

                #populating rig checkbox
                if chk[7]=='0':
                    valVar=False
                elif chk[7]=='2':
                    valVar=True
                cmds.checkBox('assetTrackRigCheck',e=True,v=valVar)

                #populating description
                cmds.scrollField('assetDescription',e=True,tx=chk[8])
                #populating notes
                for cht in ramAssetCore.listAssetNotes():
                    if cht[1]==str(chk[0]):
                        cmds.textScrollList('notesList',e=True,a=cht[4])

                #populating last handler
                for chr in ramAssetCore.listLogTable():
                    if chr[2]==assetNameVar:cmds.textField('assetLastHandler',e=True,tx=chr[1])

        #populating preview png
        for chk in ramAssetCore.listAssetTable():
            if chk[1]==str(assetNameVar):pathVar=chk[4]
        if os.path.isfile(pathVar+'/preview.png'):
            cmds.picture('screenshotPicture',e=True,image=pathVar+'/preview.png')
        else:
            cmds.picture('screenshotPicture',e=True,image=rootPathVar+'/NA.png')
        return

    #this function change asset status
    def changeAssetStatus(self,stageVar):
        #get asset name
        assetNameVar=cmds.textScrollList('assetTextScroll',q=True,si=True)
        if assetNameVar==None:
            cmds.confirmDialog(icn='warning', t='Error', m='No asset selected from asset list.', button=['Ok'])
            self.populateTable()
            raise StandardError, 'error : no asset selected from asset list'
        assetNameVar=assetNameVar[0]

        #parsing stage and change the status respectively
        if stageVar=='model':
            statusVar=cmds.checkBox('assetTrackModelCheck',q=True,v=True)
            if statusVar==True:
                statusVar=2
            else:
                statusVar=0
            ramAssetCore.updateAssetRecord(name=assetNameVar,modelStat=statusVar)
        elif stageVar=='shader':
            statusVar=cmds.checkBox('assetTrackShaderCheck',q=True,v=True)
            if statusVar==True:
                statusVar=2
            else:
                statusVar=0
            ramAssetCore.updateAssetRecord(name=assetNameVar,shaderStat=statusVar)
        elif stageVar=='rig':
            statusVar=cmds.checkBox('assetTrackRigCheck',q=True,v=True)
            if statusVar==True:
                statusVar=2
            else:
                statusVar=0
            ramAssetCore.updateAssetRecord(name=assetNameVar,rigStat=statusVar)
        self.listLegacyAndPicture()
        return

    #this function upload asset to server
    def uploadAsset(self,*args):
        #get asset name
        assetNameVar=cmds.textScrollList('assetTextScroll',q=True,si=True)
        if assetNameVar==None:
            cmds.confirmDialog(icn='warning', t='Error', m='No asset selected from asset list.', button=['Ok'])
            raise StandardError, 'error : no asset selected from asset list'
        assetNameVar=assetNameVar[0]

        #get asset type
        assetTypeVar=''
        for chk in ramAssetCore.listAssetTable():
            if chk[1]==str(assetNameVar):assetTypeVar=chk[2]
        if assetTypeVar=='':
            cmds.confirmDialog(icn='warning', t='Error', m='Cannot find record for '+str(assetNameVar)+'!',\
                               button=['Ok'])
            raise ValueError, 'error : database anomaly record non exists'

        #get asset mode
        repVar=cmds.confirmDialog(icn='question', t='Save As', m='This will upload current asset to server. Select asset stage.',\
                                  button=['MODEL','SHADER','RIG','CANCEL'])

        #uploading instruction
        if repVar!='CANCEL':
            if repVar=='MODEL':
                mode=0
            elif repVar=='SHADER':
                mode=1
            elif repVar=='RIG':
                mode=2

            if mode==0:
                mode='model'
            elif mode==1:
                mode='shader'
            elif mode==2:
                mode='rig'

            if assetTypeVar=='CHAR':
                assetTypeVar=0
            elif assetTypeVar=='PROP':
                assetTypeVar=1
            elif assetTypeVar=='SETS':
                assetTypeVar=2

            try:
                ramAssetCore.uploadAsset(name=assetNameVar,assetType=assetTypeVar,assetTarget=mode)
                cmds.confirmDialog(icn='information', t='Done', m='Asset uploaded.', button=['Ok'])
            except Exception as e:
                cmds.confirmDialog(icn='warning', t='Error', m=str(e), button=['Ok'])
                raise StandardError, str(e)

            cmds.layoutDialog(ui=self.takePicture)

        #refresh
        self.listLegacyAndPicture()
        return

    #this function download asset from server
    def downloadAsset(self,*args):
        #get asset name
        assetNameVar=cmds.textScrollList('assetTextScroll',q=True,si=True)
        if assetNameVar==None:
            cmds.confirmDialog(icn='warning', t='Error', m='No asset selected from asset list.', button=['Ok'])
            raise StandardError, 'error : no asset selected from asset list'
        assetNameVar=assetNameVar[0]

        #get asset type
        assetTypeVar=''
        for chk in ramAssetCore.listAssetTable():
            if chk[1]==str(assetNameVar):
                assetTypeVar=chk[2]
        if assetTypeVar=='':
            cmds.confirmDialog(icn='warning', t='Error', m='Cannot find record for '+str(assetNameVar)+'!',\
                               button=['Ok'])
            raise ValueError, 'error : database anomaly record non exists'

        #confirm proceeding
        #get asset mode
        repVar=cmds.confirmDialog(icn='question', t='Save As', m='Select asset stage.',\
                                  button=['MODEL','SHADER','RIG','CANCEL'])
        #download instruction
        if repVar!='CANCEL':
            if repVar=='MODEL':
                mode=0
            elif repVar=='SHADER':
                mode=1
            elif repVar=='RIG':
                mode=2

            if mode==0:
                mode='model'
            elif mode==1:
                mode='shader'
            elif mode==2:
                mode='rig'

            if assetTypeVar=='CHAR':
                assetTypeVar=0
            elif assetTypeVar=='PROP':
                assetTypeVar=1
            elif assetTypeVar=='SETS':
                assetTypeVar=2

            try:
                ramAssetCore.downloadAsset(name=assetNameVar,assetType=assetTypeVar,assetTarget=mode)
            except Exception as e:
                cmds.confirmDialog(icn='warning', t='Error', m='File did not exists', button=['Ok'])
                raise StandardError, str(e)
        #refresh
        self.listLegacyAndPicture()
        return

    #refresh function
    def refreshFun(self, *args):
        import ramAssetUI
        reload (ramAssetUI)
        return

    #register new asset function to process data from the ui module
    def registerNewAssetRecord(self,*args):
        #get data credential
        assetNewNameVar=cmds.textField('assetNewName',q=True,tx=True)
        assetNewKeyVar=cmds.textField('assetNewKey',q=True,tx=True)
        assetNewOptionVar=cmds.optionMenu('assetNewOption',q=True,v=True)
        assetNewStageVar=cmds.optionMenu('assetNewStage',q=True,v=True)
        assetNewDescriptionVar=cmds.scrollField('newAssetScrollField',q=True,tx=True)

        #validate data credential
        if assetNewNameVar=='' or assetNewKeyVar=='' or assetNewOptionVar=='' or assetNewStageVar=='' or assetNewDescriptionVar=='':
            cmds.confirmDialog(icn='warning', t='Error', m='Incomplete credential!',btn=['Ok'])
            cmds.deleteUI('ramAssetRegisterNew', window=True)
            raise StandardError, 'error : incomplete credential'

        #clear UI window
        cmds.deleteUI('ramAssetRegisterNew', window=True)

        #confirmation of the proceeding
        repVar=cmds.confirmDialog(icn='question',t='Register Asset',\
                                  m='Register asset with the following credentials:\n'\
            'Asset Name\t:'+assetNewNameVar+'\n'+\
            'Asset Key\t:'+assetNewKeyVar+'\n'+\
            'Asset Type\t:'+assetNewOptionVar+'\n'+\
            'Asset Stage\t:'+assetNewStageVar,button=['Proceed','Cancel'])

        #record registration proceeding
        if repVar=='Proceed':
            if assetNewOptionVar=='CHAR':
                assetNewOptionVar=0
            elif assetNewOptionVar=='PROP':
                assetNewOptionVar=1
            elif assetNewOptionVar=='SETS':
                assetNewOptionVar=2

            try:
                #register record
                ramAssetCore.registerAssetRecord(name=assetNewNameVar,\
                                                 keyword=assetNewKeyVar,\
                                                 type=assetNewOptionVar,description=assetNewDescriptionVar)

                #upload current file
                ramAssetCore.uploadAsset(name=assetNewNameVar,assetType=assetNewOptionVar,\
                                         assetTarget=assetNewStageVar)
            except Exception as e:
                self.refreshFun()
                raise StandardError, 'error : '+str(e)

        cmds.confirmDialog(icn='information',t='Done',m='Asset has been registered',button=['OK'])
        self.refreshFun()
        return

    #UI module to register new asset
    def registerNewAssetUI(self,*args):
        if cmds.window('ramAssetRegisterNew', exists=True):
            cmds.deleteUI('ramAssetRegisterNew', window=True)

        cmds.window('ramAssetRegisterNew',t='Register New Asset', s=False,mxb=False,mnb=False)
        cmas=cmds.columnLayout(adj=True)

        cmds.rowColumnLayout(nc=2,cw=[(1,60),(2,220)])
        cmds.text(l='Name : ',fn='boldLabelFont', al='left')
        cmds.textField('assetNewName',w=220)
        cmds.text(l='Keyword : ',fn='boldLabelFont', al='left')
        cmds.textField('assetNewKey',w=220)
        cmds.text(l='')
        cmds.text(l='note : separate keyword with comma',al='left',fn='smallObliqueLabelFont')
        cmds.text(l='Type : ',fn='boldLabelFont', al='left')
        cmds.optionMenu('assetNewOption',w=220)
        cmds.menuItem(l='')
        cmds.menuItem(l='CHAR')
        cmds.menuItem(l='PROP')
        cmds.menuItem(l='SETS')
        cmds.text(l='Stage : ',fn='boldLabelFont', al='left')
        cmds.optionMenu('assetNewStage',w=220)
        cmds.menuItem(l='')
        cmds.menuItem(l='model')
        cmds.menuItem(l='shader')
        cmds.menuItem(l='rig')

        cmds.text(l='Descript : ',fn='boldLabelFont', al='left')
        cmds.scrollField('newAssetScrollField',wordWrap=True,h=100)

        cmds.separator(p=cmas)
        cmds.button(l='REGISTER AND UPLOAD',p=cmas,c=self.registerNewAssetRecord)

        cmds.showWindow()
        return

#call main classes
ramAssetUIClass()