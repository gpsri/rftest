import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread, SIGNAL
from rftestui import Ui_rftestui
from stbcom import TestCommnad, SkedTelnet, buildCommandList, command_list,SkedSerial
# telnet program example
import socket, select, string, threading, time
from threading import Thread, Lock
import xml.etree.ElementTree as ET
import serial.tools.list_ports as port_list
#from sklearn import tree
import re
import signal

from Queue import Queue

exitFlag = 0
hddtestCnt =0
hddtestFlag = 0

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class getPTCThread(QThread):
    def __init__(self,msgQ ,telnetObj,serialObj ,option,value, msg ):
        QThread.__init__(self)
        self.msgQ = msgQ
        self.option = option
        self.value  = value
        self.msg = msg
        self.telnetObj = telnetObj
        self.serialObj = serialObj
        self.powerTestMode = 0

    def __del__(self):
        self.wait()

    def ptc_update_msg(self,option,result,value, msg):
        self.emit(SIGNAL("uiUpdateProcess(QString,QString,QString,QString)"),option, result,value, msg)

    def run(self):
        while self.runThread:
            msg = self.msgQ.get()
            print " %s " % msg
            if(msg == "startRfTest"):
                self.ptcPerformRfTest()
            elif(msg == "stopRfPowerTest"):
                self.ptcRfPowerTestStop()
            elif(msg == "startRfPowerTestCh11"):
                self.ptcPerformRfPowerTestCh11()
            elif(msg == "startRfPowerTestCh15"):
                self.ptcPerformRfPowerTestCh15()
            elif(msg == "startRfPowerTestCh20"):
                self.ptcPerformRfPowerTestCh20()
            elif(msg == "startRfPowerTestCh25"):
                self.ptcPerformRfPowerTestCh25()

            self.sleep(1)
            self.msgQ.task_done()

    def startThread(self):
        self.runThread = 1
    def stopThread(self):
        self.runThread = 0

    def ptcRfPowerTestStop(self):
        if self.powerTestMode != 0 :
            self.powerTestMode = 0
            stbPowerTestInfo = stbStopChannelPowerTesting(self,self.telnetObj,self.serialObj)
            if stbPowerTestInfo !='':
                self.ptc_update_msg("updatePowerLevelResult","PASS",stbPowerTestInfo,"")
            else:
                self.ptc_update_msg("updatePowerLevelResult","FAIL","","")

    def ptcPerformRfPowerTestCh11(self):
        if self.powerTestMode == 0 :
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,1,11)
            self.powerTestMode = 1
        else:
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,0,11)

        if stbPowerTestInfo !='':
            self.ptc_update_msg("updatePowerLevelResult","PASS",stbPowerTestInfo,"")
        else:
            self.ptc_update_msg("updatePowerLevelResult","FAIL","","")

    def ptcPerformRfPowerTestCh15(self):
        if self.powerTestMode == 0 :
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,1,15)
            self.powerTestMode = 1
        else:
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,0,15)

        if stbPowerTestInfo !='':
            self.ptc_update_msg("updatePowerLevelResult","PASS",stbPowerTestInfo,"")
        else:
            self.ptc_update_msg("updatePowerLevelResult","FAIL","","")

    def ptcPerformRfPowerTestCh20(self):
        if self.powerTestMode == 0 :
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,1,20)
            self.powerTestMode = 1
        else:
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,0,20)

        if stbPowerTestInfo !='':
            self.ptc_update_msg("updatePowerLevelResult","PASS",stbPowerTestInfo,"")
        else:
            self.ptc_update_msg("updatePowerLevelResult","FAIL","","")


    def ptcPerformRfPowerTestCh25(self):
        if self.powerTestMode == 0 :
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,1,25)
            self.powerTestMode = 1
        else:
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,0,25)

        if stbPowerTestInfo !='':
            self.ptc_update_msg("updatePowerLevelResult","PASS",stbPowerTestInfo,"")
        else:
            self.ptc_update_msg("updatePowerLevelResult","FAIL","","")

    def ptcPerformRfTest(self):

        stbSnInfo = stbGetSerialNumber(self, self.telnetObj)
        if stbSnInfo !='':
            #self.updateSerialNumberInfo(stbSnInfo[0],stbSnInfo[1])
            self.ptc_update_msg("updateSerialNumberInfo","PASS",stbSnInfo[0],stbSnInfo[1])

        #Get the Software Version
        stbSoftwareVer = stbGetSoftwareVersion(self, self.telnetObj)
        if stbSoftwareVer !='':
            self.ptc_update_msg("updateSoftwareVersion","PASS",stbSoftwareVer,"")
        else:
            self.ptc_update_msg("updateSoftwareVersion","FAIL",stbSoftwareVer,"")
        '''
        # Dump UEC Code
        stbDumpInfo = stbDumpUecCode(self,self.telnetObj)
        if stbDumpInfo !='':
            self.ptc_update_msg("updateUecCodeDump","PASS",stbDumpInfo,"")
        else:
            self.ptc_update_msg("updateUecCodeDump","FAIL","","")

        # Usb Test
        stbUsbInfo = stbPerformUsbTest(self,self.telnetObj)
        if stbUsbInfo !='':
            self.ptc_update_msg("updateUsbTestResult","PASS",stbUsbInfo,"")
        else:
            self.ptc_update_msg("updateUsbTestResult","FAIL","","")

        #Fan test
        stbFanInfo = stbPerformFanTest(self,self.telnetObj)
        if stbFanInfo !='':
            speedlist = re.findall(r'\d+', stbFanInfo)
            speedValue = int(speedlist[0])
            stbFanInfo = "SPEED : " + "%s"  % speedValue
            if speedValue < 2150 or speedValue > 4150:
                resultValue = 0
                self.ptc_update_msg("updateFanTestResult","FAIL",stbFanInfo,"")
            else:
                resultValue = 1
                self.ptc_update_msg("updateFanTestResult","PASS",stbFanInfo,"")
        else:
            self.ptc_update_msg("updateFanTestResult","FAIL","","")

        #Sata test
        stbHddInfo = stbPerformHddTest(self,self.telnetObj)
        if stbHddInfo !='':
            self.ptc_update_msg("updateHddTestResult","PASS",stbHddInfo,"")
        else:
            self.ptc_update_msg("updateHddTestResult","FAIL","","")

        #Hdmi_output test
        stbHdmiOutInfo = stbPerformHdmiTest(self, self.telnetObj)
        if stbHdmiOutInfo !='':
            self.ptc_update_msg("updateHdmiOuputTestResult","PASS",stbHdmiOutInfo,"")
        else:
            self.ptc_update_msg("updateHdmiOuputTestResult","FAIL","","")

        stbProgramMacAdd = stbProgramMacAddress(self, self.telnetObj)
        if stbProgramMacAdd !='':
            self.ptc_update_msg("updateMacAddressResult","PASS",stbProgramMacAdd,"")
        else:
            self.ptc_update_msg("updateMacAddressResult","FAIL","","")

        stbMocaTestInfo = stbPerformMocaTest(self,self.telnetObj,self.serialObj)
        if stbMocaTestInfo !='':
            self.ptc_update_msg("updateMocaResult","PASS",stbMocaTestInfo,"")
        else:
            self.ptc_update_msg("updateMocaResult","FAIL","","")
        '''
        stbZigBeeTestInfo = stbPerformZigBeeTest(self,self.telnetObj,self.serialObj)

        if stbZigBeeTestInfo !='':
            resultList = re.findall(r'\d+', stbZigBeeTestInfo)
            rxVal = int(resultList[0])
            avgRSSI = int(resultList[1])
            avgLQI = int(resultList[2])
            print rxVal
            print avgRSSI
            print avgLQI
            stbZigBeeTestInfo = "RX ="+str(rxVal)+ ":" + "Avg RSSI:"+ str(avgRSSI) + " Avg LQI:" + str(avgLQI)
            if rxVal == 0 and avgLQI == 0:
                self.ptc_update_msg("updateZigBeeResult","FAIL",stbZigBeeTestInfo,"")
            else:
                self.ptc_update_msg("updateZigBeeResult","PASS",stbZigBeeTestInfo,"")
        else:
            self.ptc_update_msg("updateZigBeeResult","FAIL","","")


class SkedYesUI(QtGui.QMainWindow):
    def __init__(self, parent= None):
        QtGui.QDialog.__init__(self,parent)

        self.ui = Ui_rftestui()

        self.ui.setupUi(self)
        self.initResetDefaultValues()
        self.ui.buttonGoldenSampleConnect.clicked.connect(self.connectToGsStb)
        self.ui.buttonDutConnect.clicked.connect(self.connectToDut)
        self.ui.buttonDutDisconnect.clicked.connect(self.disconnectFromDut)
        self.msgQ = Queue()
        buildCommandList()

    def initResetDefaultValues(self):
        ports = list(port_list.comports())
        for p in ports:
            if(p[2] != 'n/a'):
                self.ui.goldenSampleIfList.addItem(str(p[0]))

        self.ui.dutIpAddressText.setPlainText("192.192.192.2")


    def disconnectFromDut(self):
        self.telnetObj.telWrite('\x03') #ctrl + c
        time.sleep(1)
        self.telnetObj.telWrite("exit") #Exit
        self.ptcHandlingThread.stopThread()
        self.ui.buttonDutConnect.setEnabled(True)
        self.ui.buttonDutDisconnect.setEnabled(False)
        self.updateDutConnectionStatus(" Not Connected ")
        self.clearTestResults()

    def connectToGsStb(self):
        print "Connecting to COM Port  ... "
        comport = str(self.ui.goldenSampleIfList.currentText())
        '''
        print sys.platform
        if sys.platform == "linux2" or sys.platform == "linux":
            if comport == 'COM1':
                comport = '/dev/ttyUSB0'
            elif comport == 'COM2':
                comport = '/dev/ttyUSB1'
            elif comport == 'COM3':
                comport = '/dev/ttyUSB2'
            elif comport == 'COM4':
                comport = '/dev/ttyUSB3'
            elif comport == 'COM5':
                comport = '/dev/ttyUSB4'
            else:
                comport = "COM1"
        '''
        self.serialObj = SkedSerial(comport)

        print str(self.serialObj)
        print "connectToGsStb : Connected "
        self.updateGsConnectionStatus("Connected")
        stbPrepareGsRfTest(self,self.serialObj)

    def clearTestResults(self):
        self.ui.caChipNumValueLabel.clear()
        self.ui.caStbIdValueLabel.clear()
        self.ui.rfTestResultValueLabel.clear()
        self.ui.htpVersionValue.clear()
        self.ui.htpVersionResult.clear()
        self.ui.htpVersionResult.hide()
        self.ui.dumpUecCodeValue.clear()
        self.ui.dumpCodeResult.clear()
        self.ui.dumpCodeResult.hide()
        self.ui.usbValue.clear()
        self.ui.usbResult.clear()
        self.ui.usbResult.hide()
        self.ui.fanValue.clear()
        self.ui.fanResult.clear()
        self.ui.fanResult.hide()
        self.ui.sataValue.clear()
        self.ui.sataResult.clear()
        self.ui.sataResult.hide()
        self.ui.hdmiValue.clear()
        self.ui.hdmiResult.clear()
        self.ui.hdmiResult.hide()
        self.ui.dutMacAddress.clear()
        self.ui.macResult.clear()
        self.ui.macResult.hide()
        self.ui.dutMocaRestult.clear()
        self.ui.mocaResult.clear()
        self.ui.mocaResult.hide()
        self.ui.dutZigbeeResult.clear()
        self.ui.zigbeeResult.clear()
        self.ui.zigbeeResult.hide()
        self.ui.powerTestValue.hide()
        self.ui.radioButtonCHStop.setChecked(True)

    def connectToDut(self):
        print "Connecting to telnet ... "
        self.telnetObj = SkedTelnet()
        print "Connected "
        self.updateDutConnectionStatus("Connected")
        option = ""
        value = ""
        msg = ""
        self.ptcHandlingThread = getPTCThread(self.msgQ,self.telnetObj, self.serialObj, option,value,msg)
        self.connect(self.ptcHandlingThread, SIGNAL("uiUpdateProcess(QString,QString,QString,QString)"),self.uiUpdateProcess)
        self.ui.buttonDutDisconnect.clicked.connect(self.disconnectFromDut)
        self.ui.radioButtonCHStop.clicked.connect(self.stopPowerLevelTesting)
        self.ui.radioButtonCH11.clicked.connect(self.powerLevelChangeCh11)
        self.ui.radioButtonCH15.clicked.connect(self.powerLevelChangeCh15)
        self.ui.radioButtonCH20.clicked.connect(self.powerLevelChangeCh20)
        self.ui.radioButtonCH25.clicked.connect(self.powerLevelChangeCh25)
        self.ptcHandlingThread.start()
        self.ptcHandlingThread.startThread()
        self.ui.buttonDutConnect.setEnabled(False)
        self.ui.buttonDutDisconnect.setEnabled(True)
        self.msgQ.put("startRfTest")
        # auto test enabled
        #self.ptcPerformRfTest()
    def stopPowerLevelTesting(self):
        self.msgQ.put("stopRfPowerTest")

    def powerLevelChangeCh11(self):
        self.msgQ.put("startRfPowerTestCh11")

    def powerLevelChangeCh15(self):
        self.msgQ.put("startRfPowerTestCh15")

    def powerLevelChangeCh20(self):
        self.msgQ.put("startRfPowerTestCh20")

    def powerLevelChangeCh25(self):
        self.msgQ.put("startRfPowerTestCh25")

    def ptc_update_systemInfo(self):
        stbSoftwareVer = stbGetSoftwareVersion(self, self.telnetObj)
        if stbSoftwareVer !='':
            self.ptc_update_msg("updateSoftwareVersion",stbSoftwareVer,"")


    def uiUpdateProcess( self, option,result,value, msg ):
        if(option == "updateClock"):
            self.updateClock(value)
        elif(option == "updateSerialNumberInfo"):
            self.updateSerialNumberInfo(result,value,msg)
        elif(option == "updateSoftwareVersion"):
            self.updateSwVersion(result,value)
        elif(option == "updateUecCodeDump"):
            self.updateUecCodeDump(result,value)
        elif (option == "updateUsbTestResult"):
            self.updateUsbTestResult(result,value)
        elif (option == "updateFanTestResult"):
            self.updateFanTestResult(result,value)
        elif(option == "updateHddTestResult"):
            self.updateHddTestResult(result,value)
        elif(option == "updateHdmiOuputTestResult"):
            self.updateHdmiOuputTestResult(result,value)
        elif(option == "updateMacAddressResult"):
            self.updateMacAddressResult(result,value)
        elif(option == "updateMocaResult"):
            self.updateMocaResult(result,value)
        elif(option == "updateZigBeeResult"):
            self.updateZigBeeResult(result,value)
        elif(option == "updatePowerLevelResult"):
            self.updatePowerLevelResult(result,value)


    def updateGsConnectionStatus(self,text):
        if text == "Connected":
            self.ui.goldenSampleConnectionLabel.setText("GS Connected")
        else:
            self.ui.goldenSampleConnectionLabel.setText("GS Not Connected")

    def updateDutConnectionStatus(self,text):
        if text == "Connected":
            self.ui.dutConnectionLabel.setText("DUT Connected")
        else:
            self.ui.dutConnectionLabel.setText("DUT Not Connected")


    def updateSwVersion(self,result,text):
        self.ui.htpVersionValue.setOverwriteMode(True)
        self.ui.htpVersionValue.setPlainText(text)
        self.ui.htpVersionValue.setReadOnly(True)

        if result == "PASS":
            self.ui.htpVersionResult.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.htpVersionResult.setText("PASS")
        else:
            self.ui.htpVersionResult.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.htpVersionResult.setText("FAIL")
        self.ui.htpVersionResult.show()

    def updateUecCodeDump(self,result,text):
        self.ui.dumpUecCodeValue.setOverwriteMode(True)
        self.ui.dumpUecCodeValue.setPlainText(text)
        self.ui.dumpUecCodeValue.setReadOnly(True)
        if result == "PASS":
            self.ui.dumpCodeResult.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.dumpCodeResult.setText("PASS")
        else:
            self.ui.dumpCodeResult.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.dumpCodeResult.setText("FAIL")
        self.ui.dumpCodeResult.show()

    def updateUsbTestResult(self, result, text):
        self.ui.usbValue.setOverwriteMode(True)
        self.ui.usbValue.setPlainText(text)
        self.ui.usbValue.setReadOnly(True)
        if result == "PASS":
            self.ui.usbResult.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.usbResult.setText("PASS")
        else:
            self.ui.usbResult.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.usbResult.setText("FAIL")
        self.ui.usbResult.show()

    def updateFanTestResult(self, result, text):

        self.ui.fanValue.setOverwriteMode(True)
        self.ui.fanValue.setPlainText(text)
        self.ui.fanValue.setReadOnly(True)
        if result == "PASS":
            self.ui.fanResult.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.fanResult.setText("PASS")
        else:
            self.ui.fanResult.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.fanResult.setText("FAIL")
        self.ui.fanResult.show()

    def updateHddTestResult(self,result,text):
        self.ui.sataValue.setOverwriteMode(True)
        self.ui.sataValue.setPlainText(text)
        self.ui.sataValue.setReadOnly(True)
        if result == "PASS":
            self.ui.sataResult.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.sataResult.setText("PASS")
        else:
            self.ui.sataResult.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.sataResult.setText("FAIL")
        self.ui.sataResult.show()

    def updateHdmiOuputTestResult(self,result,text):
        self.ui.hdmiValue.setOverwriteMode(True)
        self.ui.hdmiValue.setPlainText(text)
        self.ui.hdmiValue.setReadOnly(True)
        if result == "PASS":
            self.ui.hdmiResult.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.hdmiResult.setText("PASS")
        else:
            self.ui.hdmiResult.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.hdmiResult.setText("FAIL")
        self.ui.hdmiResult.show()

    def updateMacAddressResult(self,result,text):
        self.ui.dutMacAddress.setOverwriteMode(True)
        self.ui.dutMacAddress.setPlainText(text)
        self.ui.dutMacAddress.setReadOnly(True)
        if result == "PASS":
            self.ui.macResult.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.macResult.setText("PASS")
        else:
            self.ui.macResult.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.macResult.setText("FAIL")
        self.ui.macResult.show()

    def updateMocaResult(self,result,text):
        self.ui.dutMocaRestult.setOverwriteMode(True)
        self.ui.dutMocaRestult.setPlainText(text)
        self.ui.dutMocaRestult.setReadOnly(True)
        if result == "PASS":
            self.ui.mocaResult.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.mocaResult.setText("PASS")
        else:
            self.ui.mocaResult.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.mocaResult.setText("FAIL")
        self.ui.mocaResult.show()

    def updatePowerLevelResult(self,result,text):
        self.ui.powerTestValue.clear()
        self.ui.powerTestValue.setText(text)
        self.ui.powerTestValue.show()

    def updateZigBeeResult(self,result,text):
        print " updateZigBeeResult"
        self.ui.dutZigbeeResult.setOverwriteMode(True)
        self.ui.dutZigbeeResult.setPlainText(text)
        self.ui.dutZigbeeResult.setReadOnly(True)
        if result == "PASS":
            self.ui.zigbeeResult.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.zigbeeResult.setText("PASS")
        else:
            self.ui.zigbeeResult.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.zigbeeResult.setText("FAIL")
        self.ui.zigbeeResult.show()
        print " updateZigBeeResult End"

    def updateSerialNumberInfo(self,result,caId,chipNumber):
        self.ui.caStbIdValueLabel.setStyleSheet(_fromUtf8("QLabel { background-color : white; color : green; }"))
        self.ui.caChipNumValueLabel.setStyleSheet(_fromUtf8("QLabel { background-color : white; color : green; }"))
        self.ui.caStbIdValueLabel.setText(caId)
        self.ui.caChipNumValueLabel.setText(chipNumber)

    def updateTestResult(self, value):
        self.ui.rfTestResultValueLabel.setText(value)

    def updateUsbTestProgress(self,text, value):
        self.ui.usbTestProgressBar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("USB Test :")
        self.ui.statusMsgLabel.setText(text)

    def updateFanTestSpeed(self,text):
        self.ui.fanSpeed.setText(text)

    def updateModelName(self, text):
        self.ui.textStbModel.setText(text)

def stbPerformMocaTest(app,tel,ser):
    findstr= "RX THROUGHPUT PASS"
    tel.telWrite('\x03') #ctrl + c
    time.sleep(.2)
    tel.telWrite(command_list[TestCommnad.MOCA_TEST_CMD1])
    time.sleep(.2)
    data = tel.telReadSocket(app)
    tel.telWrite(command_list[TestCommnad.MOCA_TEST_CMD2])
    time.sleep(1)
    data = tel.telReadSocket(app)
    tel.telWrite(command_list[TestCommnad.MOCA_TEST_CMD3])
    data = tel.telReadSocket(app)
    print data
    print "going to wait for 15 secs to complete the THROUGHPUT test "
    time.sleep(15)
    tel.telWrite(command_list[TestCommnad.MOCA_TEST_CMD3])
    data = tel.telReadSocket(app)
    match = re.search(findstr,data)
    print [data]
    if match :
        print "MOCA PASS "
        return data
    else :
        print "MOCA FAIL"
        return ''

def stbPerformZigBeeTest(app,tel,ser):
    findstr= "Avg RSSI"
    findstrInit = "PAN"
    findstrChSet = "Channel set to "
    respondFound = 0
    # Type the following commands in DUT
    #GP510GP510_transceiver 2
    # ch 20
    # an 0
    # R
    # rx 1

    #Setup DUT for Zigbee test
    print " Setup DUT for Zigbee Test"
    tel.telWrite('\x03') #ctrl + c
    time.sleep(.2)
    tel.telWrite("GP510_transceiver 2")
    time.sleep(2)
    data = tel.telReadSocket(app)
    match = re.search(findstrInit,data)
    if match:
        #Init done
        tel.telWrite("ch 20")
        time.sleep(1)
        data = tel.telReadSocket(app)
        #Channel Set OK
        tel.telWrite("an 0")
        time.sleep(1)
        data = tel.telReadSocket(app)
        tel.telWrite("R") # Reset RX and TX counters
        time.sleep(1)
        data = tel.telReadSocket(app)

        tel.telWrite("rx 1") # Enable Receiver rx 1
        time.sleep(1)
        data = tel.telReadSocket(app)
        print data


    #golden sample setup
    print "Golden Sample Setup start "
    #send the Command to Golden Sample
    ser.serWrite('\x03') #ctrl + c
    time.sleep(1)
    ser.serWrite("GP510_transceiver 2")
    time.sleep(2)
    data = ser.serRead(app)
    match = re.search(findstrInit,data)
    if match:
        #Init done
        ser.serWrite("ch 20")
        time.sleep(1)
        data = ser.serRead(app)
        #Channel Set OK
        ser.serWrite("an 0")
        time.sleep(1)
        data = ser.serRead(app)
        ser.serWrite("w 3") # set TX Power
        time.sleep(1)
        data = ser.serRead(app)
        print " Start sending 1000 packets every 10 ms"
        ser.serWrite("tx 1000 10")
        time.sleep(1)
        serData = ser.serRead(app)
        print serData

        print "DUT Setup Done "

        respondFound = 0
        retrycnt = 0
        while retrycnt < 15 and respondFound == 0:
            tel.telWrite("P")
            time.sleep(5)
            data = tel.telReadSocket(app)
            match = re.search(findstr,data)
            if match :
                print "ZigBee PASS "
                respondFound = 1
            else :
                retrycnt +=1

    if respondFound :
        print "ZigBee PASS "
    else :
        print "ZigBee FAIL"

    tel.telWrite("rx 0")
    time.sleep(1)
    tel.telWrite('\x03') #ctrl + c
    time.sleep(1)
    ser.serWrite('\x03') #ctrl + c
    time.sleep(1)
    value = data.split('\n')
    for i in value:
        print [i]

    if respondFound:
        # Expected response:
        #RX 1000 - Check this line
        #TX OK 0
        #TX Fail 0
        strRX = str(value[1])
        strRSSI = str (value[4])
        retValue = strRX + strRSSI
        return retValue
    else:
        print " Return msg 2"
        return ''
'''
def stbPerformZigBeeTest(app,tel,ser):
    findstr= "Avg RSSI"
    findstrInit = "PAN"
    findstrChSet = "Channel set to "

    #golden sample setup
    print "Golden Sample Setup start "
    #send the Command to Golden Sample
    ser.serWrite('\x03') #ctrl + c
    time.sleep(.2)
    ser.serWrite(command_list[TestCommnad.RF_TEST_INIT_COMMAND])
    time.sleep(2)
    data = ser.serRead(app)
    match = re.search(findstrInit,data)
    print [data]
    if match:
        #Init done
        cmd = command_list[TestCommnad.RF_CH_SEL_CMD] + "20" #channel number
        ser.serWrite(cmd)
        time.sleep(1)
        data = ser.serRead(app)
        #Channel Set OK
        ser.serWrite(command_list[TestCommnad.RF_ANT_SEL_CMD])
        time.sleep(1)
        data = ser.serRead(app)
        ser.serWrite(command_list[TestCommnad.GS_ZIGBEE_PING_TEST_CMD1]) # set TX Power
        time.sleep(1)
        data = ser.serRead(app)

    #Setup DUT for Zigbee test
    print " Setup DUT for Zigbee Test"
    tel.telWrite('\x03') #ctrl + c
    time.sleep(.2)
    tel.telWrite(command_list[TestCommnad.RF_TEST_INIT_COMMAND])
    time.sleep(2)
    data = tel.telReadSocket(app)
    match = re.search(findstrInit,data)
    print [data]
    if match:
        #Init done
        cmd = command_list[TestCommnad.RF_CH_SEL_CMD] + "20" #channel number
        tel.telWrite(cmd)
        time.sleep(1)
        data = tel.telReadSocket(app)
        #Channel Set OK
        tel.telWrite(command_list[TestCommnad.RF_ANT_SEL_CMD])
        time.sleep(1)
        data = tel.telReadSocket(app)
        tel.telWrite(command_list[TestCommnad.DUT_ZIGBEE_PING_TEST_CMD1]) # Reset RX and TX counters
        time.sleep(1)
        data = tel.telReadSocket(app)

        print " Start sending 1000 packets every 10 ms"
        ser.serWrite(command_list[TestCommnad.GS_ZIGBEE_PING_TEST_CMD2])
        time.sleep(1)
        serData = ser.serRead(app)
        print serData

        tel.telWrite(command_list[TestCommnad.DUT_ZIGBEE_PING_TEST_CMD2]) # Enable Receiver rx 1
        time.sleep(1)
        data = tel.telReadSocket(app)
        print data

        print "DUT Setup Done "

        respondFound = 0
        retrycnt = 0
        while retrycnt < 15 and respondFound == 0:
            tel.telWrite(command_list[TestCommnad.DUT_ZIGBEE_PING_TEST_STAT_CMD])
            time.sleep(5)
            data = tel.telReadSocket(app)
            print [data]
            match = re.search(findstr,data)
            if match :
                print "ZigBee PASS "
                respondFound = 1
            else :
                retrycnt +=1

    if respondFound :
        print "ZigBee PASS "
    else :
        print "ZigBee FAIL"

    tel.telWrite(command_list[TestCommnad.DUT_ZIGBEE_PING_TEST_STOP_CMD])
    time.sleep(1)
    tel.telWrite('\x03') #ctrl + c
    time.sleep(1)
    ser.serWrite('\x03') #ctrl + c
    time.sleep(1)
    value = data.split('\n')
    for i in value:
        print [i]

    if respondFound:
        # Expected response:
        #RX 1000 - Check this line
        #TX OK 0
        #TX Fail 0
        strRX = str(value[1])
        strRSSI = str (value[4])
        retValue = strRX + strRSSI
        return retValue
    else:
        print " Return msg 2"
        return ''
'''
def stbPerformChannelPowerTesting(app,tel,ser,initMode,chnum):
    findstrInit = "PAN"
    findCwustr= "Continuous Wave Unmodulated"
    findAntStr = "Selected Antenna"
    findWaveDisableStr = "Continuous Wave Disabled"
    findChSelStr = "Channel set"

    if initMode:
        tel.telWrite('\x03') #ctrl + c
        time.sleep(.2)
        tel.telWrite(command_list[TestCommnad.RF_TEST_INIT_COMMAND])
        time.sleep(2)
        data = tel.telReadSocket(app)
        match = re.search(findstrInit,data)
        print [data]
        if match:
            #Init done
            respondFound = 0
            retrycnt = 0
            while retrycnt < 15 and respondFound == 0:
                tel.telWrite(command_list[TestCommnad.RF_ANT_SEL_CMD])
                time.sleep(1)
                data = tel.telReadSocket(app)
                print [data]
                match = re.search(findAntStr,data)
                if match :
                    respondFound = 1
                else :
                    retrycnt +=1

        #Antenna Select OK
    else:# Disable the Continuous Wave
        respondFound = 0
        retrycnt = 0
        while retrycnt < 15 and respondFound == 0:
            tel.telWrite(command_list[TestCommnad.DUT_CH_PWR_TEST_STOP_CMD])
            time.sleep(1)
            data = tel.telReadSocket(app)
            print [data]
            match = re.search(findWaveDisableStr,data)
            if match :
                respondFound = 1
            else :
                retrycnt +=1

    # Set teh channel number
     #channel number
    respondFound = 0
    retrycnt = 0
    while retrycnt < 15 and respondFound == 0:
        cmd = command_list[TestCommnad.RF_CH_SEL_CMD] +str(chnum)
        tel.telWrite(cmd)
        time.sleep(1)
        data = tel.telReadSocket(app)
        print [data]
        match = re.search(findChSelStr,data)
        if match :
            respondFound = 1
        else :
            retrycnt +=1

    #Channel Set OK

    respondFound = 0
    retrycnt = 0
    while retrycnt < 15 and respondFound == 0:
        #Enable the Continuous Unmodulated wave
        tel.telWrite(command_list[TestCommnad.DUT_CH_PWR_TEST_STAT_CMD1])
        time.sleep(1)
        data = tel.telReadSocket(app)
        print [data]
        match = re.search(findCwustr,data)
        if match :
            respondFound = 1
        else :
            retrycnt +=1

    return re.sub('\W+','', data)

def stbStopChannelPowerTesting(app,tel,ser):
    findWaveDisableStr = "Continuous Wave Disabled"
    # Disable the Continuous Wave
    respondFound = 0
    retrycnt = 0
    while retrycnt < 15 and respondFound == 0:
        tel.telWrite(command_list[TestCommnad.DUT_CH_PWR_TEST_STOP_CMD])
        time.sleep(1)
        data = tel.telReadSocket(app)
        print [data]
        match = re.search(findWaveDisableStr,data)
        if match :
            respondFound = 1
        else :
            retrycnt +=1

    tel.telWrite('\x03') #ctrl + c
    time.sleep(1)

    return re.sub('\W+','', data)

def stbPrepareGsRfTest(app,ser):

    # Write MAC Address
    statusStr = "Write MAC successfully"

    ser.serWrite('\x03') #ctrl + c
    time.sleep(1)
    write_cmd = command_list[TestCommnad.WRITE_MAC] +" "+"001222FFFF30"
    ser.serWrite(write_cmd)
    time.sleep(1)
    print time.time()
    waitforfind = 1
    while waitforfind:
        data = ser.serRead(app)
        match = re.search(statusStr,data)
        if match :
            waitforfind = 0
            print data

    #Config the network
    write_cmd = "ifconfig eth0 192.192.192.1"
    ser.serWrite(write_cmd)
    time.sleep(1)
    data = ser.serRead(app)
    print data
    write_cmd = "ifconfig eth1 192.192.168.1"
    ser.serWrite(write_cmd)
    time.sleep(1)
    data = ser.serRead(app)
    print data

    write_cmd = "/root/bin/init_moca"
    ser.serWrite(write_cmd)
    time.sleep(1)
    data = ser.serRead(app)
    print data

    write_cmd = "iperf -s &"
    ser.serWrite(write_cmd)
    time.sleep(1)
    data = ser.serRead(app)
    print data

    write_cmd = "pstree"
    ser.serWrite(write_cmd)
    time.sleep(1)
    data = ser.serRead(app)
    print data


def stbProgramMacAddress( app, tel) :
    statusStr = "Write MAC successfully"

    tel.telWrite('\x03') #ctrl + c
    time.sleep(1)
    write_cmd = command_list[TestCommnad.WRITE_MAC] + " "+"001222FFFFF0"
    tel.telWrite(write_cmd)
    time.sleep(1)
    print time.time()
    waitforfind = 1
    while waitforfind:
        data = tel.telReadSocket(app)
        match = re.search(statusStr,data)
        if match :
            waitforfind = 0
            print data
            macadd = stbGetMacAddress(app,tel)
            return macadd[0]
        else:
            continue

def stbGetSoftwareVersion( app, tel) :
    tel.telWrite(command_list[TestCommnad.GET_VER])
    time.sleep(1)
    data = tel.telReadSocket(app)
    print data
    swver = data[(data.find("stb")):]
    swver =  swver.translate(None,'#')
    return swver

def stbDumpUecCode(app,tel) :
    dumpResponseString = "seconds"
    dumpMd5SumString = "UECN1_nopad_dump"
    tel.telWrite(command_list[TestCommnad.DUMP_UECCODE])
    data = tel.telReadSocket(app)
    print data
    waitforfind = 1
    while waitforfind:
        data = tel.telReadSocket(app)
        match = re.search(dumpResponseString,data)
        if match :
            waitforfind = 0
            print data
        else:
            continue

    #check and compare UEC code md5sum
    tel.telWrite(command_list[TestCommnad.CHECK_UECCODE])
    waitforfind = 1
    data1 = ""
    while waitforfind:
        data1 = tel.telReadSocket(app)
        match = re.search(dumpMd5SumString,data1)
        if match :
            waitforfind = 0
            print data1
            return data1
        else:
            continue

def stbGetSerialNumber(app, tel):

    snfindString= "/root/htp/generateSTBSN"
    tel.telWrite(command_list[TestCommnad.GET_STBSN])
    time.sleep(1)
    data = tel.telReadSocket(app)
    if data:
        match = re.search(snfindString,data)
        if match:
            data = re.sub(snfindString,'', data) # descard snfindString
            data = re.sub('root','', data) # descard snfindString
            data = re.sub('\W+','', data)
            data = re.sub('r','', data)
            print [data]

        stbid = (data[0:16])
        print [stbid]
        chipNum = (data[16:24])
        print [chipNum]
        snInfo= [stbid, chipNum ]
    return snInfo



def stbGetMacAddress( app, tel) :
    macaddrFindString = ":"
    tel.telWrite(command_list[TestCommnad.GET_MACADR])
    time.sleep(1)
    waitforfind = 1
    while waitforfind:
        data = tel.telReadSocket(app)
        if data:
            match = re.search(macaddrFindString,data)
            if match :
                waitforfind = 0
                data = data.translate(None, "read_mac.sh") # descard read_mac.sh
                ethmac = (data [2:19]) # Taken only the Eth Macaddr
                wifimac = (data [21:38]) # Taken only the Wifi Macaddr
                print list(ethmac)
                macadd= [ethmac, wifimac ]
                return macadd
            else :
                continue
        else :
            continue


def stbPerformFanTest(app,tel):
    currentProgressbarValue = 20
    fanPassString = "speed:"
    resultValue = ''
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    time.sleep(.2)
    tel.telWrite(command_list[TestCommnad.FAN_TEST_CMD1])
    time.sleep(.2)
    tel.telWrite(command_list[TestCommnad.FAN_TEST_CMD2])
    time.sleep(.2)
    tel.telWrite(command_list[TestCommnad.FAN_TEST_CMD3])
    time.sleep(.2)
    tel.telWrite(command_list[TestCommnad.FAN_TEST_CMD4])
    time.sleep(3)
    tel.telWrite(command_list[TestCommnad.FAN_TEST_CMD5])
    time.sleep(2)
    data = tel.telReadSocket(app)
    #print list(data)
    match = re.search(fanPassString,data)
    if match:
        speed = data[(data.find(fanPassString)): (data.find(fanPassString)) + 15]
        resultValue = speed

    stbStopFanTest(app,tel)
    return resultValue


def stbStopFanTest(app,tel):
    print("Fan Test Stopped")
    rmfanmodstr = "mstcgio"
    tel.telWrite('\x03') #ctrl + c
    tel.telWrite(command_list[TestCommnad.REMOVER_FAN_TEST_MODULE_CMD1])
    time.sleep(.2)
    data = tel.telReadSocket(app)
    tel.telWrite(command_list[TestCommnad.REMOVER_FAN_TEST_MODULE_CMD2])
    time.sleep(.2)
    data = tel.telReadSocket(app)
    #print list(data)
    match = re.search(rmfanmodstr,data)
    if match:
        print " Fan Module Not Removed "
    else :
        print " Fan Module Removed "


def stbPerformSmartcardTest(app,tel):
    currentProgressbarValue = 20

    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    smcPassString = "ATR Bytes received"
    smcFailString = "Test all Failed"
    smcNotInsertString = "Smartcard isn't inserted"
    app.ptc_update_msg("updateSmartcardTestProgress","Test Initiated",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.SMC_TEST])
    time.sleep(2)
    data = tel.telReadSocket(app)
    #print list(data)
    match = re.search(smcNotInsertString,data)
    if match:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateSmartcardTestProgress","Smartcard isn't inserted",str(currentProgressbarValue))
        return 0
    else:
        match1 = re.search(smcPassString,data)
        if match1:
            currentProgressbarValue = 100
            app.ptc_update_msg("updateSmartcardTestProgress","Smartcard Test Passed ",str(currentProgressbarValue))
            return 1
        else:
            match2 = re.search(smcFailString,data)
            if match2:
                currentProgressbarValue = 100
                app.ptc_update_msg("updateSmartcardTestProgress","Smartcard Test Failed ",str(currentProgressbarValue))
                return 0


def stbStopSmartcardTest(app,tel):
    print("Smartcard Test Stopped")
    tel.telWrite('\x03') #ctrl + c

def stbPerformUsbTest(app,tel):
    currentProgressbarValue = 20
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    usbPassString = "Test all PASS"
    usbPassString1 = "USB type: usb3.0"
    usbFailString = "Test all Failed"
    usbNotInsertString = "Cannot find USB storage Device"
    tel.telWrite(command_list[TestCommnad.USB_TEST])
    time.sleep(2)
    data = tel.telReadSocket(app)
    #print list(data)
    match = re.search(usbNotInsertString,data)
    if match:
        currentProgressbarValue = 100
        return ''
    else:
        match1 = re.search(usbPassString,data)
        match2 =  re.search(usbPassString1,data)
        if match1 or match2:
            currentProgressbarValue = 100
            return data
        else:
            match3 = re.search(usbFailString,data)
            if match3:
                currentProgressbarValue = 100
                return data
            else:
                return ''

def stbStopUsbTest(app,tel):
    print("USB Test Stopped")
    tel.telWrite('\x03') #ctrl + c

def stbPerformHdmiTest(app,tel):
    tel.telWrite('\x03') #ctrl + c
    tel.telWrite(command_list[TestCommnad.HDMI_OUTPUT_TEST])
    time.sleep(2)
    return "Check Video"

def stbPerformHddTest(app,tel):
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    hddTestCompleteString = "aft"
    hddTestFailString = "Sata'test is failed"

    tel.telWrite(command_list[TestCommnad.HDD_TEST])
    HddTestStartedFlag = 1

    print "Test is Progress"
    while HddTestStartedFlag: # keep read the socket untill get pass result
        data = tel.telReadSocket(app)
        match1 = re.search(hddTestCompleteString,data)
        match2 = re.search(hddTestFailString,data)
        if match1 or match2:
            print "HDD test Completed"
            HddTestStartedFlag = 0
            if match2:
                print "HDD Test Failed"
                return ''
            else:
                return data
        else :
            time.sleep(1)
            continue

def stbStopHddTest(app,tel):
    print("HDD test Stopped")
    tel.telWrite('\x03') #ctrl + c



def forceCloseApp():
    print "App Closed force"
    exitFlag = 1

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = SkedYesUI()
    myapp.setWindowTitle(_translate("RFTEST", "SKED YES V1.05", None))
    myapp.show()
    QtCore.QObject.connect(app, QtCore.SIGNAL(_fromUtf8("lastWindowClosed()")),forceCloseApp)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())
