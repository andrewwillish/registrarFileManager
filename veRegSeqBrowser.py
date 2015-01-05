__author__ = 'andrew.willis'

import maya.cmds as cmds
import asiist, os, veRegCore

#determining root path
rootPath=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

class rsmSequenceBrowser:
    def __init__(self):
        project=None
        for chk in asiist.getEnvi():
            if chk[0]=='projName': project=chk[1]

        if cmds.window('veSeqManager',exists=True):cmds.deleteUI('veSeqManager',wnd=True)

        title=cmds.window('veSeqManager',t='Sequence Manager ['+project+']', s=False)
        masSplit=cmds.rowColumnLayout(nc=2)
        sp1=cmds.columnLayout(adj=True,p=masSplit)
        cmds.frameLayout(l='Segment Browser')
        cmds.columnLayout(adj=True)
        cmds.text(l='Episode :',al='left', fn='boldLabelFont')
        cmds.textScrollList('episodeList', w=150, h=150, sc=self.popShot)
        cmds.text(l='Shot :',al='left', fn='boldLabelFont')
        cmds.textScrollList('shotList', h=265, w=150, sc=self.popInfoAndNotes)

        sp2=cmds.columnLayout(adj=True,p=masSplit)
        cmds.frameLayout(l='Shot Information',p=sp2)
        cmds.columnLayout(adj=True)
        cmds.text(l='Shot Name :', al='left',fn='boldLabelFont')
        cmds.textField('shotName', en=False)
        cmds.text(l='Last Handler :', al='left', fn='boldLabelFont')
        cmds.textField('lastHandler', en=False)
        cmds.text(l='Current Version', al='left', fn='boldLabelFont')
        cmds.textField('cureVer', en=False)
        cmds.separator()
        width=117
        cmds.rowColumnLayout(nc=3, cw=[(1,width), (2,width), (3,width)])
        cmds.button('DOWNLOAD SEQ', c=self.downloadSeq)
        cmds.button('VIEW PLAYBLAST', c=self.viewPlayblast)
        cmds.button('VIEW LOG', c=lambda*args: cmds.layoutDialog(ui=self.viewLog, t='Log'))

        mark = cmds.frameLayout(l='Notes',p=sp2)
        ps = cmds.rowColumnLayout(nc=2)
        cmds.columnLayout(adj=True)
        cmds.text(l='Notes Listing :', al='left', fn='boldLabelFont')
        cmds.textScrollList('noteListing', w=150, h=170, sc=self.popNotesParse)

        cmds.columnLayout(adj=True, p=ps)
        cmds.text(l='Notes Title :', al='left', fn='boldLabelFont')
        cmds.textField('noteTitle', en=False)
        cmds.text(l='Notes Author :', al='left', fn='boldLabelFont')
        cmds.textField('noteAuthor', en=False)
        cmds.text(l='Notes Date :', al='left', fn='boldLabelFont')
        cmds.textField('noteDate', en=False)
        cmds.separator()
        cmds.scrollField('noteMessage', w=200, h=80, en=False)

        mark2 = cmds.frameLayout(l='Legacy', p=sp2)
        cmds.columnLayout(adj=True)
        cmds.textScrollList('legacyList', h=80)

        cmds.showWindow()

        #popper
        pop = cmds.popupMenu(p=mark)
        cmds.menuItem(l='New Notes', c=lambda*args: cmds.layoutDialog(ui=self.postNotesUI, t='Log'))

        pop1 = cmds.popupMenu(p=mark2)
        cmds.menuItem(l='Load Legacy', c=self.loadLegacy)

        self.popEps()
        return

    def loadLegacy(self, *args):
        episode=cmds.textScrollList('episodeList', q=True, si=True)[0]
        shot=cmds.textScrollList('shotList', q=True, si=True)[0]
        file=cmds.textScrollList('legacyList', q=True, si=True)[0]

        veRegCore.loadLegacy(eps=episode, shot=shot, file=file)
        return

    def postNotes(self,mode):
        if mode==0:
            cmds.layoutDialog(dismiss='CANCEL')
        else:
            cmds.layoutDialog(dismiss='POST')

            episode=cmds.textScrollList('episodeList', q=True, si=True)[0]
            shot=cmds.textScrollList('shotList', q=True, si=True)[0]

            #get credential
            titleVar=cmds.textField('newNotesTitle',q=True,tx=True)
            messageVar=cmds.scrollField('newNotesMessage',q=True,tx=True)

            veRegCore.addNotes(eps=episode, shot=shot, title=titleVar, notes=messageVar)
            self.popNotes()
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

    def viewLog(self,*args):
        episode=cmds.textScrollList('episodeList', q=True, si=True)[0]
        shot=cmds.textScrollList('shotList', q=True, si=True)[0]

        #generate UI
        cmas = cmds.columnLayout(adj=True)
        cmds.textScrollList('logList', w=500, h=400)

        #populating UI
        cmds.textScrollList('logList', e=True, ra=True)
        for chk in veRegCore.listLog(eps=episode, shot=shot):
            cmds.textScrollList('logList', e=True, a=chk)
        return

    def viewPlayblast(self, *args):
        #get episode and shot data
        episode=cmds.textScrollList('episodeList', q=True, si=True)[0]
        shot=cmds.textScrollList('shotList', q=True, si=True)[0]

        #view playblast
        veRegCore.viewPlayblast(eps=episode, shot=shot)
        return

    def downloadSeq(self, *args):
        #get episode and shot data
        episode=cmds.textScrollList('episodeList', q=True, si=True)[0]
        shot=cmds.textScrollList('shotList', q=True, si=True)[0]

        #check if current scene has been saved
        if cmds.file(q=True, modified=True):
            repVar = cmds.confirmDialog(icn='question', t='Modified',\
                                        m='Current scene has been modified. Would you like to save it?',\
                                        button=['Save', 'Skip', 'Cancel'])
            if repVar == 'Skip': veRegCore.downloadSeq(eps=episode, shot=shot)
            elif repVar == 'Save': cmds.file(s=True)
        else:
            veRegCore.downloadSeq(eps=episode, shot=shot)
        return

    def popEps(self):
        cmds.textScrollList('episodeList', e=True, ra=True)
        for item in veRegCore.listEps():cmds.textScrollList('episodeList', e=True, a=str(item))
        return

    def popShot(self):
        #clear
        cmds.textField('noteTitle',e=True, tx='')
        cmds.textField('noteAuthor',e=True, tx='')
        cmds.textField('noteDate',e=True, tx='')
        cmds.scrollField('noteMessage', e=True, tx='')
        cmds.textField('shotName', e=True, tx='')
        cmds.textField('lastHandler', e=True, tx='')
        cmds.textField('cureVer', e=True, tx='')
        cmds.textScrollList('noteListing', e=True, ra=True)
        cmds.textScrollList('shotList', e=True, ra=True)
        cmds.textScrollList('legacyList', e=True, ra=True)

        cmds.textScrollList('shotList',e=True,ra=True)
        selEps=cmds.textScrollList('episodeList', q=True, si=True)
        if selEps is not None:
            selEps=selEps[0]
            for item in veRegCore.listShot(eps=selEps):
                cmds.textScrollList('shotList', e=True, a=str(item))
        return

    def popNotesParse(self):
        global noteList
        cmds.textField('noteTitle',e=True, tx='')
        cmds.textField('noteAuthor',e=True, tx='')
        cmds.textField('noteDate',e=True, tx='')
        cmds.scrollField('noteMessage', e=True, tx='')

        selectedItem = cmds.textScrollList('noteListing', q=True, si=True)
        if selectedItem != None: selectedItem = selectedItem[0]

        for item in noteList:
            if selectedItem in item:
                cmds.textField('noteTitle',e=True, tx=item[2])
                cmds.textField('noteAuthor',e=True, tx=item[0])
                cmds.textField('noteDate',e=True, tx=item[1])
                cmds.scrollField('noteMessage', e=True, tx=item[3])
        return

    def popInfoAndNotes(self):
        cmds.textField('shotName', e=True, tx='')
        cmds.textField('lastHandler', e=True, tx='')
        cmds.textField('cureVer', e=True, tx='')

        #get episode and shot data
        episode=cmds.textScrollList('episodeList', q=True, si=True)[0]
        shot=cmds.textScrollList('shotList', q=True, si=True)[0]

        #get shotInfo data
        shotInfo = veRegCore.getShotInformation(eps=episode, shot=shot)
        cmds.textField('shotName', e=True, tx=shotInfo[0][:-3])
        cmds.textField('lastHandler', e=True, tx=shotInfo[1])
        cmds.textField('cureVer', e=True, tx=shotInfo[2])

        self.popNotes()
        self.popLegacy()
        return

    def popNotes(self):
        global noteList
        #clear field
        cmds.textField('noteTitle',e=True, tx='')
        cmds.textField('noteAuthor',e=True, tx='')
        cmds.textField('noteDate',e=True, tx='')
        cmds.scrollField('noteMessage', e=True, tx='')

        #get episode and shot data
        episode=cmds.textScrollList('episodeList', q=True, si=True)[0]
        shot=cmds.textScrollList('shotList', q=True, si=True)[0]

        #get notes data
        noteList = veRegCore.listNotes(eps=episode, shot=shot)

        #populate notes data
        cmds.textScrollList('noteListing', e=True, ra=True)
        for chk in noteList:cmds.textScrollList('noteListing', e=True, a=chk[1])
        return

    def popLegacy(self):
        #get episode and shot data
        episode=cmds.textScrollList('episodeList', q=True, si=True)[0]
        shot=cmds.textScrollList('shotList', q=True, si=True)[0]

        cmds.textScrollList('legacyList', e=True, ra=True)
        parsed = veRegCore.listLegacy(eps=episode, shot=shot)
        parsed.reverse()
        for item in parsed:
            cmds.textScrollList('legacyList', e=True, a=item[:-3])
        return

rsmSequenceBrowser()