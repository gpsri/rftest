import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread, SIGNAL
from rftestui import Ui_rftestui
from stbcom import TestCommnad, SkedTelnet, buildCommandList, command_list,SkedSerial
# telnet program example
import socket, select, string, threading, time
from threading import Thread, Lock
import xml.etree.ElementTree as ET
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

    def __del__(self):
        self.wait()

    def ptc_update_msg(self,option,result,value, msg):
        self.emit(SIGNAL("uiUpdateProcess(QString,QString,QString,QString)"),option, result,value, msg)

    def run(self):
        while self.runThread:
            msg = self.msgQ.get()
            print " %s " % msg
            self.sleep(1)
            self.msgQ.task_done()

    def startThread(self):
        self.runThread = 1
    def stopThread(self):
        self.runThread = 0


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

    def initResetDefaultValues(self):
        self.ui.goldenSampleIfList.addItem("COM1")
        self.ui.goldenSampleIfList.addItem("COM2")
        self.ui.goldenSampleIfList.addItem("COM3")
        self.ui.goldenSampleIfList.addItem("COM4")
        self.ui.goldenSampleIfList.addItem("COM5")
        self.ui.dutIpAddressText.setPlainText("192.192.192.2")


    def disconnectFromDut(self):
        self.telnetObj.telWrite('\x03') #ctrl + c
        time.sleep(1)
        self.telnetObj.telWrite("exit") #Exit
        self.ptcHandlingThread.stopThread()
        self.ui.buttonDutConnect.setEnabled(True)
        self.ui.buttonDutDisconnect.setEnabled(False)
        self.updateDutConnectionStatus(" Not Connected ")

    def connectToGsStb(self):
        print "Connecting to COM Port  ... "
        self.serialObj = SkedSerial()
        print "Connected "
        self.updateGsConnectionStatus("Connected")

    def connectToDut(self):
        print "Connecting to telnet ... "
        self.telnetObj = SkedTelnet()
        print "Connected "
        self.updateDutConnectionStatus("Connected")
        buildCommandList()
        option = ""
        value = ""
        msg = ""
        self.ptcHandlingThread = getPTCThread(self.msgQ,self.telnetObj, self.serialObj, option,value,msg)
        self.connect(self.ptcHandlingThread, SIGNAL("uiUpdateProcess(QString,QString,QString,QString)"),self.uiUpdateProcess)
        self.ui.buttonDutDisconnect.clicked.connect(self.disconnectFromDut)
        self.ptcHandlingThread.start()
        self.ptcHandlingThread.startThread()
        self.ui.buttonDutConnect.setEnabled(False)
        self.ui.buttonDutDisconnect.setEnabled(True)
        # auto test enabled
        self.ptcPerformRfTest()

    def ptc_update_systemInfo(self):
        stbSoftwareVer = stbGetSoftwareVersion(self, self.telnetObj)
        if stbSoftwareVer !='':
            self.ptc_update_msg("updateSoftwareVersion",stbSoftwareVer,"")
        telReadSocke

    def ptcPerformRfTest(self):
        #Get the Software Version
        stbSoftwareVer = stbGetSoftwareVersion(self, self.telnetObj)
        if stbSoftwareVer !='':
            self.ptcHandlingThread.ptc_update_msg("updateSoftwareVersion","PASS",stbSoftwareVer,"")
        else:
            self.ptcHandlingThread.ptc_update_msg("updateSoftwareVersion","FAIL",stbSoftwareVer,"")
        # Dump UEC Code
        stbDumpInfo = stbDumpUecCode(self,self.telnetObj)
        if stbDumpInfo !='':
            self.ptcHandlingThread.ptc_update_msg("updateUecCodeDump","PASS",stbDumpInfo,"")
        else:
            self.ptcHandlingThread.ptc_update_msg("updateUecCodeDump","FAIL","","")

        # Usb Test
        stbUsbInfo = stbPerformUsbTest(self,self.telnetObj)
        if stbDumpInfo !='':
            self.ptcHandlingThread.ptc_update_msg("updateUsbTestResult","PASS",stbUsbInfo,"")
        else:
            self.ptcHandlingThread.ptc_update_msg("updateUsbTestResult","FAIL","","")

        #Fan test
        stbFanInfo = stbPerformFanTest(self,self.telnetObj)
        if stbFanInfo !='':
            self.ptcHandlingThread.ptc_update_msg("updateFanTestResult","PASS",stbFanInfo,"")
        else:
            self.ptcHandlingThread.ptc_update_msg("updateFanTestResult","FAIL","","")

        #Sata test
        stbHddInfo = stbPerformHddTest(self,self.telnetObj)
        if stbHddInfo !='':
            self.ptcHandlingThread.ptc_update_msg("updateHddTestResult","PASS",stbHddInfo,"")
        else:
            self.ptcHandlingThread.ptc_update_msg("updateHddTestResult","FAIL","","")

        #Hdmi_output test
        stbHdmiOutInfo = stbPerformHdmiTest(self. self.telnetObj)
        if stbHddInfo !='':
            self.ptcHandlingThread.ptc_update_msg("updateHdmiOuputTestResult","PASS",stbHdmiOutInfo,"")
        else:
            self.ptcHandlingThread.ptc_update_msg("updateHdmiOuputTestResult","FAIL","","")



    def uiUpdateProcess( self, option,result,value, msg ):
        if(option == "updateClock"):
            self.updateClock(value)
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
        '''
        elif(option == "updateEthMacAddr"):
            self.updateEthMac(value)
        elif(option == "updateWifiMacAddr"):
            self.updateWifiMac(value)
        elif(option == "updateModelName"):
            self.updateModelName(value)
        elif(option == "updateHddSerial"):
            self.updateHddSerailNumber(value)
        elif(option == "updateHddTestProgress"):
            self.updateHddTestProgress(value,int(msg))

        elif (option == "updateUsbTestProgress"):
            self.updateUsbTestProgress(value, int (msg))
        elif (option == "updateSmartcardTestResult"):
            self.updateSmartcardTestResult(value)
        elif (option == "updateSmartcardTestProgress"):
            self.updateSmartcardTestProgress(value, int (msg))

        elif (option == "updateFanTestProgress"):
            self.updateFanTestProgress(value, int (msg))
        elif (option == "updateLedTestResult"):
            self.updateLedTestResult(value)
        elif (option == "updateLedTestProgress"):
            self.updateLedTestProgress(value, int (msg))
        elif (option == "updateFpTestResult"):
            self.updateFpTestResult(value)
        elif (option == "updateFpTestProgress"):
            self.updateFpTestProgress(value, int (msg))
        elif (option == "updateButtonTestProgress"):
            self.updateButtonTestProgress(value, int (msg))
        elif (option == "updateButtonTestResult"):
            self.updateButtonTestResult(value)
        elif (option == "updateIrTestProgress"):
            self.updateIrTestProgress(value, int (msg))
        elif (option == "updateIrTestResult"):
            self.updateIrTestResult(value)
        elif (option == "updateFanTestSpeed"):
            self.updateFanTestSpeed(value)
        elif (option == "updateTunerTestResult"):
            self.updateTunerTestResult(value)
        elif (option == "updateTunerTestProgress"):
            self.updateTunerTestProgress(value, int (msg))
        '''
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


    def updateEthMac(self,text) :
        self.ui.textStbEth0Mac.setText(text)
        self.ui.textStbEth0Mac.setReadOnly(True)

    def updateWifiMac(self,text) :
        self.ui.textStbWifiMac.setText(text)
        self.ui.textStbWifiMac.setReadOnly(True)

    def updateClock(self,text):
        self.ui.dateAndTime.setText(text)
    def updateTemperature(self,text):
        print text
        #self.ui.labelTemperatureValue.setStyleSheet("QLabel { background-color : blue; color : white; }")
        self.ui.labelTemperatureValue.setText(text)
    def updateHddSerailNumber(self, text):
        self.ui.textStbHddSn.setText(text)

    def updateHddTestProgress(self,text, value):
        self.ui.hddTestProgressBar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("HDD Test :")
        cntstr = " Test Count %d " % hddtestCnt
        textStr = text + cntstr
        self.ui.statusMsgLabel.setText(textStr)

    def updateUsbTestProgress(self,text, value):
        self.ui.usbTestProgressBar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("USB Test :")
        self.ui.statusMsgLabel.setText(text)


    def updateSmartcardTestProgress(self,text, value):
        self.ui.smartcardTestProgressbar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("Smartcard Test :")
        self.ui.statusMsgLabel.setText(text)

    def updateSmartcardTestResult(self, text):
        if(text == "PASS"):
            self.ui.smartcardResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.smartcardResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.smartcardResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.smartcardResult.setText("FAIL")

        self.ui.smartcardStartButton.setEnabled(True)
        self.ui.smartcardStopButton.setEnabled(False)


    def updateIrTestProgress(self,text, value):
        self.ui.irTestProgressbar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("IR Test :")
        self.ui.statusMsgLabel.setText(text)

    def updateIrTestResult(self, text):
        if(text == "PASS"):
            self.ui.irResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.irResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.irResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.irResult.setText("FAIL")
        self.ui.irStartButton.setEnabled(True)
        self.ui.irStopButton.setEnabled(False)

    def updateFanTestProgress(self,text, value):
        self.ui.fanTestProgressbar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("Fan Test :")
        self.ui.statusMsgLabel.setText(text)


    def updateFanTestSpeed(self,text):
            self.ui.fanSpeed.setText(text)

    def updateLedTestResult(self, text):
        if(text == "PASS"):
            self.ui.ledResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.ledResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.ledResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.ledResult.setText("FAIL")
        self.ui.ledStartButton.setEnabled(True)
        self.ui.ledStopButton.setEnabled(False)

    def updateLedTestProgress(self,text, value):
        self.ui.ledTestProgressbar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("LED Test :")
        self.ui.statusMsgLabel.setText(text)

    def updateTunerTestResult(self, text):
        if(text == "PASS"):
            self.ui.tunerResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.tunerResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.tunerResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.tunerResult.setText("FAIL")


    def updateTunerTestProgress(self,text, value):
        self.ui.tunerTestProgressBar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("Tuner Test :")
        self.ui.statusMsgLabel.setText(text)

    def updateFpTestResult(self, text):
        if(text == "PASS"):
            self.ui.fpResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.fpResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.fpResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.fpResult.setText("FAIL")
        self.ui.fpStartButton.setEnabled(True)
        self.ui.fpStopButton.setEnabled(False)

    def updateFpTestProgress(self,text, value):
        self.ui.fpTestProgressbar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("FP Test :")
        self.ui.statusMsgLabel.setText(text)


    def updateButtonTestResult(self, text):
        if(text == "PASS"):
            self.ui.buttonResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.buttonResult.setText("PASS")
            Keystr = "Key : "
            Keystr = Keystr + "Pressed"
            self.ui.buttonKeysRecivce.setText(Keystr)
        elif(text == "FAIL"):
            self.ui.buttonResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.buttonResult.setText("FAIL")
        self.ui.buttonStartButton.setEnabled(True)
        self.ui.buttonStopButton.setEnabled(False)

    def updateButtonTestProgress(self,text, value):
        self.ui.buttonTestProgressbar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("Button Test :")
        self.ui.statusMsgLabel.setText(text)


    def updateModelName(self, text):
        self.ui.textStbModel.setText(text)

def stbGetTemperature(appThread,tel):
    tempFindString = "temp_monitor"
    tel.telWrite(command_list[TestCommnad.GET_TEMPERATURE])
    time.sleep(2)
    data = tel.telReadSocket(appThread)
    match = re.search(tempFindString,data)
    #print list(data)
    if match:
        temperature = data[(data.find("temp_monitor")):(data.find("temp_monitor"))+15]
        temperature = temperature.translate(None,"temp_monitor")
        temperature = temperature + " " + "C"
        #print temperature
        return temperature
    else:
        return "0 C"


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




def stbDiseqcSettings(app,tel, diseqcObj):
    print "Diseqc Settings is called "
    if((diseqcObj.lnb22KhzTone == 1) and (diseqcObj.lnbVoltage == 13 )):
        tel.telWrite(command_list[TestCommnad.LNB_LOW_22K_ON])
        time.sleep(1)
        data = tel.telReadSocket(app)
    elif((diseqcObj.lnb22KhzTone == 0) and (diseqcObj.lnbVoltage == 13 )):
        tel.telWrite(command_list[TestCommnad.LNB_LOW_22K_OFF])
        time.sleep(1)
        data = tel.telReadSocket(app)
    elif((diseqcObj.lnb22KhzTone == 1) and (diseqcObj.lnbVoltage == 18 )):
        tel.telWrite(command_list[TestCommnad.LNB_HIGH_22K_ON])
        time.sleep(1)
        data = tel.telReadSocket(app)
    else:
        tel.telWrite(command_list[TestCommnad.LNB_HIGH_22K_OFF])
        time.sleep(1)
        data = tel.telReadSocket(app)



def stbPerformTunerTest(app,tel):

    currentProgressbarValue = 20
    TunerTestProgress = 1
    tunerPassString = "Decoding sat"
    tunerFailString = "No channels found"
    app.ptc_update_msg("updateTunerTestProgress","Test Initiated",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.TUNE_TEST])
    time.sleep(1)
    currentProgressbarValue = currentProgressbarValue + 20
    app.ptc_update_msg("updateTunerTestProgress","Test Progress",str(currentProgressbarValue))
    time.sleep(3)
    data = tel.telReadSocket(app)
    #print list(data)
    match = re.search(tunerPassString,data)
    if match:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateTunerTestProgress","Test Done",str(currentProgressbarValue))
        return 1
    else:
        match1 = re.search(tunerFailString,data)
        if match1:
            currentProgressbarValue = 100
            app.ptc_update_msg("updateTunerTestProgress","Test Done",str(currentProgressbarValue))
            return 0
        else:
            while TunerTestProgress:
                data = tel.telReadSocket(app)
                print list(data)
                print data
                match = re.search(tunerPassString,data)
                if match:
                    TunerTestProgress = 0
                    currentProgressbarValue = 100
                    app.ptc_update_msg("updateTunerTestProgress","Test Done",str(currentProgressbarValue))
                    return 1
                else:
                    match1 = re.search(tunerFailString,data)
                    if match1:
                        currentProgressbarValue = 100
                        TunerTestProgress = 0
                        app.ptc_update_msg("updateTunerTestProgress","Test Done",str(currentProgressbarValue))
                        return 0
                    else:
                        currentProgressbarValue = currentProgressbarValue + 20
                        app.ptc_update_msg("updateTunerTestProgress","Test Progress ",str(currentProgressbarValue))
                        continue




def stbStopTunerTest(app,tel):
    tel.telWrite('\x03') #ctrl + c
    print ("Tuner_Test_Stopped")


def stbPerformFanTest(app,tel):
    currentProgressbarValue = 20
    fanPassString = "speed:"

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
    time.sleep(.2)
    tel.telWrite(command_list[TestCommnad.FAN_TEST_CMD5])
    time.sleep(.2)
    data = tel.telReadSocket(app)
    #print list(data)
    match = re.search(fanPassString,data)
    if match:

        speed = data[(data.find(fanPassString)): (data.find(fanPassString)) + 15]
        print speed
        msgStr = "FAN : " + "%s"  % speed
        print msgStr
        stbStopFanTest(app,tel)
        return msgStr
    else:

        stbStopFanTest(app,tel)
        return 0


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

def stbStopUsbTest(app,tel):
    print("USB Test Stopped")
    tel.telWrite('\x03') #ctrl + c

# ['\r', '\n', '#', ' ', 'h', 'd', 'd', 'S', 'e', 'r', 'i', 'a', 'l', 'N', 'u', 'm', 'b', 'e', 'r', '\r', '\n', 'Z', '9', 'C', '5', 'P', 'J', '9', '3', '\r', '\n', '#', ' ']
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
                return data
            else:
                return data
        else :
            time.sleep(1)
            continue

def stbStopHddTest(app,tel):
    print("HDD test Stopped")
    tel.telWrite('\x03') #ctrl + c


def stbPerformLedTest(app,tel):
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    retry = 1
    retrycnt = 0
    currentProgressbarValue = 20
    ledPassString = "LED all on"
    app.ptc_update_msg("updateLedTestProgress","Test Initiated",str(currentProgressbarValue))
    command_list[TestCommnad.LED_TEST] = "led 0"
    tel.telWrite(command_list[TestCommnad.LED_TEST])
    time.sleep(2)
    command_list[TestCommnad.LED_TEST] = "led 1"
    tel.telWrite(command_list[TestCommnad.LED_TEST])
    data = tel.telReadSocket(app)
    time.sleep(2)
    #print list(data)
    match = re.search(ledPassString,data)
    if match:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateLedTestProgress","Led Test Passed ",str(currentProgressbarValue))
        return 1
    else:
        while retry :
            data = tel.telReadSocket(app)
            time.sleep(2)
            #print list(data)
            match = re.search(ledPassString,data)
            if match:
                retry = 0
                currentProgressbarValue = 100
                app.ptc_update_msg("updateLedTestProgress","Led Test Passed ",str(currentProgressbarValue))
                return 1
            else:
                if(retrycnt > 5):
                    currentProgressbarValue =  currentProgressbarValue + 6
                    app.ptc_update_msg("updateLedTestProgress","Led Test Failed ",str(currentProgressbarValue))
                    return 0
                retrycnt = retrycnt + 1
                continue




def stbStopLedTest(app,tel):
    print("Led Test Stopped")
    command_list[TestCommnad.LED_TEST] = "led 0"
    tel.telWrite(command_list[TestCommnad.LED_TEST])
    time.sleep(2)


def stbPerformFpTest(app,tel):
    retry = 1
    retrycnt = 0
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    currentProgressbarValue = 20
    fpPassString = "act_gridon"
    app.ptc_update_msg("updateFpTestProgress","Test Initiated",str(currentProgressbarValue))
    command_list[TestCommnad.VFD_TEST] = "/root/htp/vfd -r -i -x 0"
    tel.telWrite(command_list[TestCommnad.VFD_TEST])
    time.sleep(2)
    command_list[TestCommnad.VFD_TEST] = "/root/htp/vfd -r -i -x 1"
    tel.telWrite(command_list[TestCommnad.VFD_TEST])
    data = tel.telReadSocket(app)
    time.sleep(2)
    #print list(data)
    match = re.search(fpPassString,data)
    if match:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateFpTestProgress","FP Test Passed ",str(currentProgressbarValue))
        return 1
    else:
        return 0


def stbStopFpTest(app,tel):
    print("Fp Test Stopped")
    command_list[TestCommnad.VFD_TEST] = "/root/htp/vfd -r -i -x 0"
    tel.telWrite(command_list[TestCommnad.VFD_TEST])
    time.sleep(2)


def stbPerformIrTest(app,tel):
    retry = 1
    retrycnt = 0
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    currentProgressbarValue = 20
    irPassString = "IR test: pass"
    irFailString = "IR test: failed"
    app.ptc_update_msg("updateIrTestProgress","Test Initiated",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.IR_TEST])
    time.sleep(5)
    data = tel.telReadSocket(app)
    #print list(data)
    match = re.search(irPassString,data)
    if match:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateIrTestProgress","IR Test Passed ",str(currentProgressbarValue))
        return 1
    else:
        match = re.search(irFailString,data)
        if match:
            currentProgressbarValue = 100
            app.ptc_update_msg("updateIrTestProgress","IR Test Failed ",str(currentProgressbarValue))
            return 0
        else:
            while retry :
                data = tel.telReadSocket(app)
                time.sleep(2)
                #print list(data)
                match = re.search(irPassString,data)
                if match:
                    retry = 0
                    currentProgressbarValue = 100
                    app.ptc_update_msg("updateIrTestProgress","IR Test Passed ",str(currentProgressbarValue))
                    return 1
                else:
                    match = re.search(irFailString,data)
                    if match:
                        currentProgressbarValue = 100
                        app.ptc_update_msg("updateIrTestProgress","IR Test Failed ",str(currentProgressbarValue))
                        return 0
                    elif(retrycnt > 5):
                        currentProgressbarValue =  currentProgressbarValue + 6
                        app.ptc_update_msg("updateIrTestProgress","Waiting for IR-Key Press ",str(currentProgressbarValue))
                        return 0
                retrycnt = retrycnt + 1
                continue




def stbStopIrTest(app,tel):
    print("IR Test Stopped")
    tel.telWrite(command_list[TestCommnad.STOP_TUNE_TEST]) # ctrl +c to stop
    time.sleep(2)

def stbPerformButtonTest(app,tel):
    retry = 1
    retrycnt = 0
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    currentProgressbarValue = 20
    buttonPassString = "Button1 pass 1"
    buttonFailString = "Button1 Failed 0"
    app.ptc_update_msg("updateButtonTestProgress","Test Initiated",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.BUTTON_TEST])
    time.sleep(.5)
    data = tel.telReadSocket(app)
    time.sleep(.5)
    #print list(data)
    match = re.search(buttonPassString,data)
    if match:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateButtonTestProgress","Button Test Passed ",str(currentProgressbarValue))
        return 1
    else:
        match = re.search(buttonFailString,data)
        if match:
            currentProgressbarValue = 100
            app.ptc_update_msg("updateButtonTestProgress","Button Test Failed ",str(currentProgressbarValue))
            return 0
        else:
            while retry :
                data = tel.telReadSocket(app)
                time.sleep(2)
                #print list(data)
                match = re.search(buttonPassString,data)
                if match:
                    retry = 0
                    currentProgressbarValue = 100
                    app.ptc_update_msg("updateButtonTestProgress","Button Test Passed ",str(currentProgressbarValue))
                    return 1
                else:
                    match = re.search(buttonFailString,data)
                    if match:
                        currentProgressbarValue = 100
                        app.ptc_update_msg("updateButtonTestProgress","Button Test Failed ",str(currentProgressbarValue))
                        return 0
                    elif(retrycnt > 5):
                        currentProgressbarValue =  currentProgressbarValue + 6
                        app.ptc_update_msg("updateButtonTestProgress","Waiting for button Press ",str(currentProgressbarValue))
                        return 0
                retrycnt = retrycnt + 1
                continue




def stbStopButtonTest(app,tel):
    print("Button Test Stopped")
    tel.telWrite(command_list[TestCommnad.STOP_TUNE_TEST]) # ctrl +c to stop
    time.sleep(2)


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
    myapp.setWindowTitle(_translate("SkedYes", "SKED YES V1.03", None))


    myapp.show()
    #myapp.updateConnectionStatus("Not Connected ")
    '''
    buildCommandList()
    tel.telWrite("ls \n")
    data = tel.telReadSocket(myapp)
    print data
    getSerialNumber(myapp, tel)
    getMacAddress(myapp, tel)
    performHDDTest(myapp, tel)

    skedPtcAppThread.startThread()
    skedPtcAppThread.start()
    '''
    #QtCore.QObject.connect(self.StartButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.labelHDDTestSetFocus)
    #QtCore.QObject.connect(myapp.ui.StopButton, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), disconectTheSTB)
    QtCore.QObject.connect(app, QtCore.SIGNAL(_fromUtf8("lastWindowClosed()")),forceCloseApp)
    #QtCore.QObject.connect(myapp.ui.StartButton, QtCore.SIGNAL(_fromUtf8("clicked()")), connectTheSTB)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())