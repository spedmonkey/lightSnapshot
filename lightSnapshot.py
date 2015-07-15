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

def getMayaWindow():                        
    ptr=mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class BasicDialog(QtGui.QDialog):
    #Start GUI
    def __init__(self, parent=getMayaWindow()):
        super(BasicDialog, self).__init__(parent)

        self.sceneDirectory=(cmds.file(q=1, sn=1)).rsplit('/', 1)[0]
        self.mayaScene=(cmds.file(q=1, sn=1)).rsplit('/', 1)[-1]
        
        self.setWindowTitle("lightSnapshot")
        self.shapeTypeCB=QtGui.QComboBox(parent=self)
        #self.populateCB()
       
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
        
        self.populateCB()
        self.changeLabels()
          
        #Connecting Signals
        self.connect(self.shapeTypeCB, QtCore.SIGNAL("currentIndexChanged(int)"), self.changeLabels)           
        self.connect(self.saveBtn, QtCore.SIGNAL("clicked()"), self.saveButton)
        self.connect(self.loadBtn, QtCore.SIGNAL("clicked()"), self.loadAttr)

    def populateCB(self):
        for i in self.readData():
                self.shapeTypeCB.addItem (i[0] [i[0].keys()[0]]['snapShotDescription']) 
        print "=========================================================="
        print "==========================LOADING========================="
        print "=========================================================="
         
    def changeLabels(self): 
        try:
            version = self.shapeTypeCB.currentIndex()
            firstLight=self.readData()[version][0].keys()[0]
            self.scenelbl.setText (self.readData()[version][0][firstLight]['snapShotScene'])
            self.timelbl.setText (self.readData()[version][0][firstLight]['snapShottime']) 
        except:
            print 'failed to change labels'       

    def readData(self):
        try:
            with open (self.sceneDirectory+"/lightSnapshot.json") as data_file:
                lightSnapshot=json.load(data_file)
        except:
            lightSnapshot = []       
        return  lightSnapshot
    
    def loadAttr(self):
        lightSnapshot=self.readData()
        version = self.shapeTypeCB.currentIndex()
        
        #index is the index of the combo box
        myDic=lightSnapshot[version][0]
        
        #setShape Values
        for key, value in myDic.items():
            for extrakey, extravalue in value.items(): 
                try:
                    if isinstance (extravalue, basestring) == True:
                        if extravalue == 'None':
                            extravalue = ''
                            exec ("pm.PyNode('{0}').{1}.set('{2}')".format (key, extrakey, extravalue))
                            print ("pm.PyNode('{0}').{1}.set('{2}')".format (key, extrakey, extravalue)) + " VALUE SET"
                            
                        else: 
                            exec ("pm.PyNode('{0}').{1}.set('{2}')".format (key, extrakey, extravalue))
                            print ("pm.PyNode('{0}').{1}.set('{2}')".format (key, extrakey, extravalue)) + " VALUE SET"                            
                    else:    
                        exec ("pm.PyNode('{0}').{1}.set({2})".format (key, extrakey, extravalue))
                        print ("pm.PyNode('{0}').{1}.set({2})".format (key, extrakey, extravalue)) + " VALUE SET"
                except:
                    pass

        #setTransform Values                       
        for key, value in myDic.items():
            for extrakey, extravalue in value.items(): 
                try:
  
                    exec ("pm.PyNode('{0}').{1}.set({2})".format (key, extrakey, extravalue) )
                except:
                    pass

    def saveButton(self):
        if self.textDialog()!='cancelled':
            self.shapeTypeCB.clear()
            self.writeLightLister()
            self.populateCB()
        else:
            print "Cancelled Save"
       
    def textDialog(self):      
        myVar=""
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter Description:')
        if ok:
            self.description = str(text)
        else:
            self.description = 'cancelled'
        return self.description
        
    def getLights(self):
    
        #change to type of lights
        areaLights=pm.ls(type='wmAreaLightNode')
        ibl=pm.ls(type='wmImageBasedLightNode')
        blockers = pm.ls(type='wmGoboNode')
        myLights=areaLights+ibl+blockers
        return myLights
                 
    def writeLightLister(self):
        tempList=[]
        
        try:
            lightSnapshot=self.readData()   
        except:
            print 'failed to read'
            lightSnapshot=[]
        
        lightDic={}

        for i in self.getLights():
            lightDic[i.name()]={}
            lightDic[ str(i.listRelatives(p=1)[0]) ]={}
            
            mayaScene=self.mayaScene
            
            #Define Attributes
            self.snapShotTime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            #create dictionary  
            #create shape dictionary
            for attribute in i.listAttr():
                try: 
                    lightDic[i.name()][attribute.rsplit('.', 1)[1]]=str(attribute.get())
                except:
                    pass
            #Add custom attributes / meta information to shape      
            lightDic[i.name()]['snapShotDescription']=self.description
            lightDic[i.name()]['snapShotScene']=self.mayaScene
            lightDic[i.name()]['snapShottime']=self.snapShotTime  
            #create transform dictionary
            for transforms in i.listRelatives(p=1)[0].listAttr():
                try:
                    lightDic[ str(i.listRelatives(p=1)[0])] [str(transforms.rsplit('.', 1)[1])]=str(transforms.get())
                except:
                    pass
            #Add custom attributes / meta information to transform
            lightDic[ str(i.listRelatives(p=1)[0])]['snapShotDescription']=self.description
            lightDic[ str(i.listRelatives(p=1)[0])]['snapShotScene']=self.mayaScene
            lightDic[ str(i.listRelatives(p=1)[0])]['snapShottime']=self.snapShotTime
            
            #append ditionary to list
            tempList.append(lightDic)
            
        lightSnapshot=[tempList]+lightSnapshot
        
        with open(self.sceneDirectory+"/lightSnapshot.json", mode="w") as feedsjson:
            json.dump(lightSnapshot, feedsjson, indent=4) 
            feedsjson.write('\n') 

        print "=========================================================="
        print "==========================SAVING=========================="
        for i in self.getLights():
            print 'Saving '+i
        print "=========================================================="