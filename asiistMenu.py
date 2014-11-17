__author__ = 'Andrewwillish'

import maya.cmds as cmds
import os, imp, sys
import maya.mel as mel

#Determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#module launcher
def moduleLauncher(name,path):
    imp.load_compiled(name,path) if path.endswith('.pyc')==True else imp.load_source(name,path)
    return

#get main window name
mainWindow = mel.eval('$temp1=$gMainWindow')

#build menu tree
try:
    cmds.menu('m_registrarMenu',l='Registrar File Manager', tearOff=True,p=mainWindow)
except:
    pass

cmds.menuItem('assetManager',l='Asset Manager',p='m_registrarMenu',\
              c=lambda*args: moduleLauncher('assetManager',rootPathVar+'/ramAssetUI.py'))
cmds.menuItem(divider=True)
cmds.menuItem('shotSetup',l='Shot Setup',p='m_registrarMenu',\
              c=lambda*args: moduleLauncher('assetManager',rootPathVar+'/rsmShotSetup.py'))
cmds.menuItem('shotBuilder',l='Shot Builder',p='m_registrarMenu',\
              c=lambda*args: moduleLauncher('assetManager',rootPathVar+'/rsmShotBuilder.py'))
cmds.menuItem(divider=True)