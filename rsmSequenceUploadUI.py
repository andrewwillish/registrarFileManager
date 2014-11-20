__author__ = 'andrew.willis'

import maya.cmds as cmds
import asiist, os, rsmSequenceCore
import rsmSequenceCore

class rsmSequenceUploadUI:
    def __init__(self):
        repVar=cmds.confirmDialog(icn='information',\
                                  t='Sequence Upload',\
                                  message='This will upload current scene file to server. Proceed?',\
                                  button=['Proceed','Cancel'])
        if repVar=='Proceed':self.uploadSeq()
        return

    def uploadSeq(self):
        try:
            rsmSequenceCore.uploadSeq()
        except Exception as e:
            cmds.confirmDialog(icn='warning',t='Error',m=str(e),button=['Ok'])
        return

rsmSequenceUploadUI()