__author__ = 'spedmonkey'
'''
import method

import sys
sys.path.append ('/usr/home/crussell/Documents/python/lightSnapshot')

import masterTest
reload (masterTest)
masterTest.BasicDialog().show()

'''
import maya.cmds as cmds
import maya.OpenMayaUI as mui
from PyQt4 import QtCore, QtGui
import sip
import pymel.core as pm
import json
import datetime

lightDic = {}
myTime=datetime.datetime.now()
mayaScene=cmds.file(q=True, sn=1, shortName=True)
lightSnapshot=[]

def getMayaWindow():
    ptr=mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class BasicDialog(QtGui.QDialog):
    #def global variables
    #lightSnapshot=[]
    #Start GUI
    def __init__(self, parent=getMayaWindow()):
        super(BasicDialog, self).__init__(parent)
        self.setWindowTitle("lightSnapshot")
        self.shapeTypeCB=QtGui.QComboBox(parent=self)
        self.populateCB()

        #createWidgets
        self.timelbl=QtGui.QLabel("description", parent=self)
        self.scenelbl=QtGui.QLabel("scene", parent=self)
        self.loadBtn=QtGui.QPushButton("Load")
        self.saveBtn=QtGui.QPushButton("Save")

        #Layout Widgets
        actionLayout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight, self)
        actionLayout.addWidget(self.shapeTypeCB)

        actionLayout.addWidget(self.timelbl)
        actionLayout.addWidget(self.scenelbl)
        actionLayout.addWidget(self.loadBtn)
        actionLayout.addWidget(self.saveBtn)

        #Connecting Signals
        self.connect(self.shapeTypeCB, QtCore.SIGNAL("currentIndexChanged(int)"), self.changeLabels)
        self.connect(self.saveBtn, QtCore.SIGNAL("clicked()"), self.saveButton)
        self.connect(self.loadBtn, QtCore.SIGNAL("clicked()"), self.loadAttr)

    def populateCB(self):
        try:
            for i in self.readData():
                print i[str(myLights[0])][6][1]
                self.shapeTypeCB.addItem(i[str(myLights[0])][6][1])
        except:
            print 'failed to read file'

    def changeLabels(self):
        self.timelbl.setText (self.readData()[self.shapeTypeCB.currentIndex()][str(myLights[0])][3][1] )
        self.scenelbl.setText (self.readData()[self.shapeTypeCB.currentIndex()][str(myLights[0])][6][1] )

    def readData(self):
        try:
            with open ("/usr/home/crussell/Documents/python/lightSnapshot/test.json") as data_file:
                lightSnapshot=json.load(data_file)
                print 'data read'
        except:
            lightSnapshot = "couldn't open file"
        return lightSnapshot


    def loadAttr(self):
        lightSnapshot=self.readData()
        try:
                #NEED TO CHANGE [-1] TO INDEX OF COMBO BOX
            for i in self.readData()[self.shapeTypeCB.currentIndex()]:
                print i

                #CREATE pyNode and variables
                myLight = pm.PyNode(i)
                notes=lightSnapshot[self.shapeTypeCB.currentIndex()][i][6][1]

                exposure=lightSnapshot[self.shapeTypeCB.currentIndex()][i][1][1]
                lightColor=lightSnapshot[self.shapeTypeCB.currentIndex()][i][2][1]
                snapTime=lightSnapshot[self.shapeTypeCB.currentIndex()][i][3][1]

                #print lightColor
                translate=lightSnapshot[self.shapeTypeCB.currentIndex()][i][4][1]
                rotate=lightSnapshot[self.shapeTypeCB.currentIndex()][i][5][1]

                #Set Attr
                myLight.exposure.set(exposure)
                myLight.lightColor.set(lightColor)

                myLight.listRelatives(p=1)[0].translate.set(translate)
                myLight.listRelatives(p=1)[0].rotate.set(rotate)

                if myLight.hasAttr('notes'):
                    myLight.notes.set(notes)
                else:
                    myLight.addAttr('notes', dt='string')
                    myLight.notes.set(notes)
        except:
            for i in self.readData()[0]:
                print i
            print 'failed to create pynode'
            pass

    def saveButton(self):
        self.textDialog()
        self.shapeTypeCB.clear()
        self.writeLightLister()
        self.populateCB()

    def textDialog(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter Description:')
        if ok:
            self.notes=text

    def getLights(self):
        #change to type of lights
        myLights=pm.ls(type='<type of light>')
        return myLights

    def writeLightLister(self):
        for i in self.getLights():
            #Define Attributes
            lightTrans = pm.xform(i.listRelatives(p=1), ws=1, t=1, q=1)
            lightRot =  pm.xform(i.listRelatives(p=1), ws=1, ro=1, q=1)
            #lightScale=  pm.xform(i.listRelatives(p=1), ws=1, s=1, q=1)
            exposure = i.exposure.get()
            lightColor = i.lightColor.get()
            lightDic[i.name()] = [ ["name",i.name()], ["exposure", exposure], ["color",lightColor], ["time", str(myTime)], ["translate", lightTrans], ["rotate", lightRot],["notes", str(self.notes)],["scene", mayaScene] ]

        try:
            lightSnapshot=self.readData()
            lightSnapshot.append(lightDic)
        except:
            lightSnapshot=[]
            lightSnapshot.append(lightDic)

        with open("/usr/home/crussell/Documents/python/lightSnapshot/test.json", mode="w") as feedsjson:
            json.dump(lightSnapshot, feedsjson, indent=4)
            feedsjson.write('\n')
        print 'data saved'