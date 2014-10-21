__author__ = 'andrew.willis'

#Registrar Asset Manager - Setup Console

import ramSetupCore
import sys, os

os.system('cls')

class ramSetupConsole:
    def __init__(self):
        #Welcome message
        print 'Registrar Asset Manager 2.0 - Setup Console'
        print ''
        #invoking main menu looping around to keep asking for new order
        while True:
            commandVar=raw_input('Insert Command >> ')

            os.system('cls')

            print 'Registrar Asset Manager 2.0 - Setup Console'
            print ''
            #Parsing command
            if commandVar=='exit':
                sys.exit(0)
            elif commandVar=='':
                pass
            elif commandVar=='help':
                self.printHelp()
            elif commandVar=='setup':
                self.setupFun()
            elif commandVar=='setupAssetRoot':
                self.setupAssetRoot()
            elif commandVar=='setupSequenceRoot':
                self.setupSequenceRoot()
            else:
                print ('invalid command')
            print ''
        return

    def setupSequenceRoot(self):
        pathVar=raw_input('Enter root path for sequence server: ')
        if pathVar=='':
            print ('path is empty')
        ramSetupCore.setRootPath(sequencialRootPath=pathVar)
        print ('RAM sequencial root set')
        return

    def setupAssetRoot(self):
        pathVar=raw_input('Enter root path for asset server: ')
        if pathVar=='':
            print ('path is empty')
        ramSetupCore.setRootPath(assetRootPath=pathVar)
        print ('RAM asset root set')
        return

    def setupFun(self):
        ramSetupCore.setupAssetTable()
        ramSetupCore.setupLogTable()
        ramSetupCore.setupRootXml()
        ramSetupCore.setupAssetNotes()
        print ('RAM basic setup finished')
        return

    def printHelp(self):
        print ('setup \t\t\t- setup RAM dependencies')
        print ('setupAssetRoot \t\t- setup RAM asset root path')
        print ('setupSequenceRoot \t- setup RAM sequence root path')
        print ('exit \t\t\t- exit setup')
        print ('help \t\t\t- view help menu')
        return

ramSetupConsole()