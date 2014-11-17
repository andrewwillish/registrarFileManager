__author__ = 'andrew.willis'

import maya.cmds as cmds
import asiist, os, rsmSequenceCore
import ramAssetCore

#determining root path
rootPath=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

class rsmSequenceBrowser:
    def __init__(self):
        project=None
        for chk in asiist.getEnvi():
            if chk[0]=='projName':project=chk[1]

        if cmds.window('veSeqManager',exists=True):cmds.deleteUI('veSeqManager',wnd=True)

        title=cmds.window('veSeqManager',t='Sequence Manager ['+project+']', s=False)
        masSplit=cmds.rowColumnLayout(nc=2)
        sp1=cmds.columnLayout(adj=True,p=masSplit)
        cmds.frameLayout(l='Segment Browser')
        cmds.columnLayout(adj=True)
        cmds.text(l='Episode :',al='left',fn='boldLabelFont')
        cmds.textScrollList('episodeList',w=150)
        cmds.text(l='Shot :',al='left',fn='boldLabelFont')
        cmds.textScrollList('shotList',h=200,w=150)

        sp2=cmds.columnLayout(adj=True,p=masSplit)
        cmds.frameLayout(l='Shot Information',p=sp2)
        cmds.columnLayout(adj=True)
        cmds.text(l='Shot Name :',al='left',fn='boldLabelFont')
        cmds.textField('shotName',en=False)
        cmds.text(l='Last Handler :',al='left',fn='boldLabelFont')
        cmds.textField('lastHandler',en=False)
        cmds.text(l='Current Version',al='left',fn='boldLabelFont')
        cmds.textField('cureVer',en=False)
        cmds.separator()
        width=80
        cmds.rowColumnLayout(nc=4,cw=[(1,width),(2,width),(3,width),(4,width)])
        cmds.button('UPLOAD\nSEQUENCE')
        cmds.button('DOWNLOAD\nSEQUENCE')
        cmds.button('VIEW\nPLAYBLAST')
        cmds.button('VIEW\nLOG')

        cmds.frameLayout(l='Notes',p=sp2)
        ps=cmds.rowColumnLayout(nc=2)
        cmds.columnLayout(adj=True)
        cmds.text(l='Notes Listing :',al='left',fn='boldLabelFont')
        cmds.textScrollList('noteListing',w=120,h=170)

        cmds.columnLayout(adj=True,p=ps)
        cmds.text(l='Notes Title :',al='left',fn='boldLabelFont')
        cmds.textField('noteTitle',en=False)
        cmds.text(l='Notes Author :',al='left',fn='boldLabelFont')
        cmds.textField('noteAuthor',en=False)
        cmds.text(l='Notes Date :',al='left',fn='boldLabelFont')
        cmds.textField('noteDate',en=False)
        cmds.separator()
        cmds.scrollField(w=200,h=80)

        cmds.frameLayout(l='Legacy',p=sp2)
        cmds.columnLayout(adj=True)
        cmds.textScrollList('legacyList',h=80)

        cmds.showWindow()
        return

    def refresh(self):

        return

    def popEps(self):

        return


rsmSequenceBrowser()