import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread, SIGNAL
from rftestui import Ui_rftestui
from stbcom import TestCommnad, SkedTelnet, buildCommandList, command_list,SkedSerial, test_pingHOST
# telnet program example
import socket, select, string, threading, time
from threading import Thread, Lock
import xml.etree.ElementTree as ET
import serial.tools.list_ports as port_list
#from sklearn import tree
import re
import os
import signal
from shutil import copyfile

is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue as queue

#from Queue import Queue

exitFlag = 0
hddtestCnt =0
hddtestFlag = 0
resultFlag = True
zigbeeTestChannelInfo = "11"
wid = ""

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
        self.listenSTDINflag = 0
        self.reportFile = open("temp_", 'w')

    def __del__(self):
        self.wait()

    def ptc_update_msg(self,option,result,value, msg):
        self.emit(SIGNAL("uiUpdateProcess(QString,QString,QString,QString)"),option, result,value, msg)

    def run(self):
        while self.runThread:
            msg = self.msgQ.get()
            print (" %s " % msg)
            if(msg == "startRfTest"):
                self.ptcRfPowerTestStop()
            elif(msg == "startGetMSTCVersion"):
                self.ptcPerformGetSerialNumber()
                self.ptcPerformGetSoftwareVersion()
            elif(msg == "startDumpUECCode"):
                self.ptcPerformDumpUEC()
            elif(msg == "startUSBTest"):
                self.ptcPerformUSB()
            elif(msg == "startFANTest"):
                self.ptcPerformFan()
            elif(msg == "startSATATest"):
                self.ptcPerformSata()
            elif(msg == "startHDMITest"):
                self.ptcPerformHDMI()
            elif(msg == "startMACTest"):
                self.ptcPerformMAC()
            elif(msg == "startMOCATest"):
                self.ptcPerformMAC()
                self.ptcPerformMOCA()
            elif(msg == "startZIGBEETest"):
                self.ptcPerformZIGBEE()
            elif(msg == "startRfPowerTestCh11"):
                self.ptcPerformRfPowerTestCh11()
            elif(msg == "startRfPowerTestCh15"):
                self.ptcPerformRfPowerTestCh15()
            elif(msg == "startRfPowerTestCh20"):
                self.ptcPerformRfPowerTestCh20()
            elif(msg == "startRfPowerTestCh25"):
                self.ptcPerformRfPowerTestCh25()
            elif(msg == "startlnbtest"):
                self.ptcPerformLNBTest()
            elif(msg == "endTest"):
                print("test complete")
                # End
                if resultFlag == True:
                    result = "PASS"
                    self.ptc_update_msg("updateTestResult","PASS","","")
                elif resultFlag == False:
                    result = "FAIL"
                    self.ptc_update_msg("updateTestResult","FAIL","","")

                self.ptc_update_msg("updatetestEndLabel", result,"","")
                self.telnetObj.telWrite('\x03') #ctrl + c
                time.sleep(.2)
                data = self.telnetObj.telReadSocket(self)
                self.disconnectFromDut()
            elif(msg == "createReportFile"):
                print("createReportFile")
                self.reportFile = open("temp_",'w')
                if (self.reportFile == 0):
                    print("Can't create Report")
                global wid
                if (len(wid) == 10):
                    self.reportFile.write("WID="+wid+"\n")
            elif(msg == "closeReportFile"):
                self.closeReportFile()

            self.sleep(1)
            self.msgQ.task_done()

    def startThread(self):
        self.runThread = 1
    def stopThread(self):
        self.runThread = 0

    def closeReportFile(self):
        print("closeReportFileCalled")
        srcFile =str(self.reportFile.name);
        print (srcFile);
        self.reportFile.close()
        #copyfile(srcFile, "Outbuffer_tmp.txt")
        if os.path.exists(srcFile) == True :
            stbSnInfo = stbGetSerialNumber(self, self.telnetObj)
            if stbSnInfo !='':
                stbSN = str(stbSnInfo[0])
            else :
                stbSN = "NOSN"
            if os.path.exists(stbSN + ".txt") == True:
                os.remove(stbSN + ".txt")
            copyfile(srcFile, stbSN + ".txt")
            os.remove(srcFile)

    def disconnectFromDut(self):
        global resultFlag
        self.closeReportFile()
        time.sleep(1)
        self.telnetObj.telWrite('\x03') #ctrl + c
        time.sleep(1)
        self.telnetObj.telWrite("exit") #Exit
        self.ptc_update_msg("updateDutConnectionStatus", " Not Connected ", "", "")
        self.ptc_update_msg("updateConnectbotton", "PASS","", "")
        self.stopThread()
        resultFlag = True


    def ptcRfPowerTestStop(self):
        if self.powerTestMode != 0 :
            self.powerTestMode = 0
            stbPowerTestInfo = stbStopChannelPowerTesting(self,self.telnetObj,self.serialObj)
            if stbPowerTestInfo !='':
                self.ptc_update_msg("updatePowerLevelResult","PASS",stbPowerTestInfo,"")
            else:
                self.ptc_update_msg("updatePowerLevelResult","FAIL","","")

    def ptcPerformRfPowerTestCh11(self):
        global resultFlag
        if resultFlag == False :
            return

        if self.powerTestMode == 0 :
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,1,11)
            self.powerTestMode = 1
        else:
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,0,11)

        if stbPowerTestInfo !='':
            power_start = stbPowerTestInfo.find("power")
            power_end = stbPowerTestInfo.find("Mhz")
            level_end = stbPowerTestInfo.find("dBm")
            resultList = re.findall(r'[-]?\d+', stbPowerTestInfo)
            freq = int(resultList[0])
            powerlevel = int(resultList[1])
            if (powerlevel < -30 or powerlevel > -18) :
                self.ptc_update_msg("updatePowerLevelResult11","FAIL",stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm","")
                self.reportFile.write(str("PWRCH11=")+stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm "+"FAIL"'\n')
                resultFlag = False
            else :
                self.ptc_update_msg("updatePowerLevelResult11","PASS",stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm","")
                self.reportFile.write(str("PWRCH11=")+stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm"'\n')
        else:
            self.ptc_update_msg("updatePowerLevelResult11","FAIL","","")
            self.reportFile.write(str("PWRCH11=")+"0 FAIL"'\n')
            resultFlag = False

    def ptcPerformRfPowerTestCh15(self):
        global resultFlag
        if resultFlag == False :
            return
        if self.powerTestMode == 0 :
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,1,15)
            self.powerTestMode = 1
        else:
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,0,15)

        if stbPowerTestInfo !='':
            power_start = stbPowerTestInfo.find("power")
            power_end = stbPowerTestInfo.find("Mhz")
            level_end = stbPowerTestInfo.find("dBm")
            resultList = re.findall(r'[-]?\d+', stbPowerTestInfo)
            freq = int(resultList[0])
            powerlevel = int(resultList[1])
            if (powerlevel < -30 or powerlevel > -20) :
                self.ptc_update_msg("updatePowerLevelResult15","FAIL",stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm","")
                self.reportFile.write(str("PWRCH15=")+stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm "+"FAIL"'\n')
                resultFlag = False
            else :
                self.ptc_update_msg("updatePowerLevelResult15","PASS",stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm","")
                self.reportFile.write(str("PWRCH15=")+stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm"'\n')
        else:
            self.ptc_update_msg("updatePowerLevelResult15","FAIL","","")
            self.reportFile.write(str("PWRCH15=")+"0 FAIL"'\n')
            resultFlag = False

    def ptcPerformRfPowerTestCh20(self):
        global resultFlag
        if resultFlag == False :
            return
        if self.powerTestMode == 0 :
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,1,20)
            self.powerTestMode = 1
        else:
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,0,20)

        if stbPowerTestInfo !='':
            power_start = stbPowerTestInfo.find("power")
            power_end = stbPowerTestInfo.find("Mhz")
            level_end = stbPowerTestInfo.find("dBm")
            resultList = re.findall(r'[-]?\d+', stbPowerTestInfo)
            freq = int(resultList[0])
            powerlevel = int(resultList[1])
            if (powerlevel < -30 or powerlevel > -20) :
                self.ptc_update_msg("updatePowerLevelResult20","FAIL",stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm","")
                self.reportFile.write(str("PWRCH20=")+stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm "+"FAIL"'\n')
                resultFlag = False
            else :
                self.ptc_update_msg("updatePowerLevelResult20","PASS",stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm","")
                self.reportFile.write(str("PWRCH20=")+stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm"'\n')
        else:
            self.ptc_update_msg("updatePowerLevelResult20","FAIL","","")
            self.reportFile.write(str("PWRCH20=")+"0 FAIL"'\n')
            resultFlag = False


    def ptcPerformLNBTest(self):
        global resultFlag
        if resultFlag == False :
            return
        stblnbtestinfo = stbPerformLNBTest(self,self.telnetObj,self.serialObj)
        if stblnbtestinfo == 1:
            self.ptc_update_msg("updatelnbtest", "1", "0", "")
            self.reportFile.write("LNB Test Pass"+'\n')
        else :
            self.ptc_update_msg("updatelnbtest", "0", "0", "")
            self.reportFile.write("LNB Test Fail"+'\n')

    def ptcPerformRfPowerTestCh25(self):
        global resultFlag
        if resultFlag == False :
            return
        if self.powerTestMode == 0 :
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,1,25)
            self.powerTestMode = 1
        else:
            stbPowerTestInfo = stbPerformChannelPowerTesting(self,self.telnetObj,self.serialObj,0,25)

        if stbPowerTestInfo !='':
            power_start = stbPowerTestInfo.find("power")
            power_end = stbPowerTestInfo.find("Mhz")
            level_end = stbPowerTestInfo.find("dBm")
            resultList = re.findall(r'[-]?\d+', stbPowerTestInfo)
            freq = int(resultList[0])
            powerlevel = int(resultList[1])
            if (powerlevel < -30 or powerlevel > -20) :
                self.ptc_update_msg("updatePowerLevelResult25","FAIL",stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm","")
                self.reportFile.write(str("PWRCH25=")+stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm "+"FAIL"'\n')
                resultFlag = False
            else :
                self.ptc_update_msg("updatePowerLevelResult25","PASS",stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm","")
                self.reportFile.write(str("PWRCH25=")+stbPowerTestInfo[power_start:power_end]+"Mhz" + stbPowerTestInfo[power_end+3:level_end] + "dBm"'\n')
        else:
            self.ptc_update_msg("updatePowerLevelResult25","FAIL","","")
            self.reportFile.write(str("PWRCH25=")+"0 FAIL"'\n')
            resultFlag = False

    def ptcPerformGetSerialNumber(self):
        global resultFlag
        if resultFlag == False :
            return
        stbSnInfo = stbGetSerialNumber(self, self.telnetObj)
        if stbSnInfo !='':
            #self.updateSerialNumberInfo(stbSnInfo[0],stbSnInfo[1])
            self.ptc_update_msg("updateSerialNumberInfo","PASS",stbSnInfo[0],stbSnInfo[1])
            #filename = str(stbSnInfo[0]+".txt")
            self.stbSN = str(stbSnInfo[0])
            if(self.reportFile == 0):
                print("ERROR FILE OPEN")
                resultFlag = False
            else:
                self.reportFile.write(str("CASSTBID="+stbSnInfo[0])+'\n')
                self.reportFile.write(str("CHIPNUM="+stbSnInfo[1])+'\n')

    def ptcPerformGetSoftwareVersion(self):
        #Get the Software Version
        global resultFlag
        if resultFlag == False :
            return
        stbSoftwareVer = stbGetSoftwareVersion(self, self.telnetObj)
        if stbSoftwareVer !='':
            self.ptc_update_msg("updateSoftwareVersion","PASS",stbSoftwareVer,"")
            self.reportFile.write(str("MSTCHTPVERSION="+stbSoftwareVer)+'\n')
        else:
            self.ptc_update_msg("updateSoftwareVersion","FAIL",stbSoftwareVer,"")
            self.reportFile.write(str("MSTCHTPVERSION=0")+'\n')
            resultFlag = False

    def ptcPerformDumpUEC(self):
        # Dump UEC Code
        global resultFlag
        if resultFlag == False :
            return
        stbDumpInfo = stbDumpUecCode(self,self.telnetObj)
        if stbDumpInfo !='':
            self.ptc_update_msg("updateUecCodeDump","PASS",stbDumpInfo,"")
            self.reportFile.write(str("UECCODEMD5="+stbDumpInfo)+'\n')
        else:
            self.ptc_update_msg("updateUecCodeDump","FAIL","","")
            self.reportFile.write(str("UECCODEMD5=0")+'\n')
            resultFlag = False

    def ptcPerformUSB(self):
        global resultFlag
        if resultFlag == False :
            return
        # Usb Test
        stbUsbInfo = stbPerformUsbTest(self,self.telnetObj)
        if stbUsbInfo !='':
            self.ptc_update_msg("updateUsbTestResult","PASS",stbUsbInfo,"")
            self.reportFile.write(str("USB=1")+'\n')
        else:
            self.ptc_update_msg("updateUsbTestResult","FAIL","","")
            self.reportFile.write(str("USB=0")+'\n')
            resultFlag = False

    def ptcPerformFan(self):
        global resultFlag
        if resultFlag == False :
            return
        #Fan test
        stbFanInfo = stbPerformFanTest(self,self.telnetObj)
        if stbFanInfo !='':
            speedlist = re.findall(r'\d+', stbFanInfo)
            speedValue = int(speedlist[0])
            stbFanInfo = "SPEED : " + "%s"  % speedValue
            if speedValue < 2150 or speedValue > 4150:
                resultValue = 0
                self.ptc_update_msg("updateFanTestResult","FAIL",stbFanInfo,"")
                self.reportFile.write(str("FAN=0")+'\n')
                resultFlag = False
            else:
                resultValue = 1
                self.ptc_update_msg("updateFanTestResult","PASS",stbFanInfo,"")
                self.reportFile.write(str("FAN=1")+'\n')
        else:
            self.ptc_update_msg("updateFanTestResult","FAIL","","")
            self.reportFile.write(str("FAN=0")+'\n')
            resultFlag = False


    def ptcPerformSata(self):
        global resultFlag
        if resultFlag == False :
            return
        #Sata test
        stbHddInfo = stbPerformHddTest(self,self.telnetObj)
        if stbHddInfo !='':
            self.ptc_update_msg("updateHddTestResult","PASS",stbHddInfo,"")
            self.reportFile.write(str("HDD=1")+'\n')
        else:
            self.ptc_update_msg("updateHddTestResult","FAIL","","")
            self.reportFile.write(str("HDD=0")+'\n')
            resultFlag = False


    def ptcPerformHDMI(self):
        global resultFlag
        if resultFlag == False :
            return
        #Hdmi_output test
        stbHdmiOutInfo = stbPerformHdmiTest(self, self.telnetObj)
        if stbHdmiOutInfo !='':
            self.ptc_update_msg("updateHdmiOuputTestResult","PASS",stbHdmiOutInfo,"")
            self.reportFile.write(str("HDMI=1")+'\n')
        else:
            self.ptc_update_msg("updateHdmiOuputTestResult","FAIL","","")
            self.reportFile.write(str("HDMI=0")+'\n')
            resultFlag = False

    def ptcPerformMAC(self):
        global resultFlag
        if resultFlag == False :
            return
        stbProgramMacAdd = stbProgramMacAddress(self, self.telnetObj)
        if stbProgramMacAdd !='':
            self.ptc_update_msg("updateMacAddressResult","PASS",stbProgramMacAdd,"")
        else:
            self.ptc_update_msg("updateMacAddressResult","FAIL","","")
            resultFlag = False

    def ptcPerformMOCA(self):
        global resultFlag
        if resultFlag == False :
            return
        stbMocaTestInfo = stbPerformMocaTest(self,self.telnetObj,self.serialObj)
        if stbMocaTestInfo !='':
            self.ptc_update_msg("updateMocaResult","PASS",stbMocaTestInfo,"")
            self.reportFile.write(str("MOCA=1")+'\n')
        else:
            self.ptc_update_msg("updateMocaResult","FAIL","","")
            self.reportFile.write(str("MOCA=0")+'\n')
            resultFlag = False

    def ptcPerformZIGBEE(self):
        global resultFlag
        if resultFlag == False :
            return
        stbZigBeeTestInfo = stbPerformZigBeeTest(self,self.telnetObj,self.serialObj)
        if stbZigBeeTestInfo !='':
            resultList = re.findall(r'[-]?\d+', stbZigBeeTestInfo)
            rxVal = int(resultList[0])
            avgRSSI = int(resultList[1])
            avgLQI = int(resultList[2])
            print (rxVal)
            print (avgRSSI)
            print (avgLQI)
            stbZigBeeTestInfo = "RX ="+str(rxVal)+ ":" + "Avg RSSI:"+ str(avgRSSI) + " Avg LQI:" + str(avgLQI)
            if rxVal >= 990 and rxVal <= 1050 and avgRSSI >= -80 and avgRSSI <= 1 and avgLQI >= -10 and avgLQI <= 80:
                self.ptc_update_msg("updateZigBeeResult","PASS",stbZigBeeTestInfo,"")
                self.reportFile.write(str("ZIGBEE=1")+'\n')
            else:
                self.ptc_update_msg("updateZigBeeResult","FAIL",stbZigBeeTestInfo,"")
                self.reportFile.write(str("ZIGBEE=0")+'\n')
                resultFlag = False
        else:
            self.ptc_update_msg("updateZigBeeResult","FAIL","","")
            self.reportFile.write(str("ZIGBEE=0")+'\n')
            resultFlag = False

    def ptcPerformRfTest(self):
        # End
        if resultFlag == True:
            result = "PASS"
            self.ptc_update_msg("updateTestResult","PASS","","")
        elif resultFlag == False:
            result = "FAIL"
            self.ptc_update_msg("updateTestResult","FAIL","","")

        self.ptc_update_msg("updatetestEndLabel", result,"","")
        self.telnetObj.telWrite('\x03') #ctrl + c
        time.sleep(.2)
        data =self.telnetObj.telReadSocket(self)

class SkedYesUI(QtGui.QMainWindow):
    def __init__(self, parent= None):
        QtGui.QDialog.__init__(self,parent)

        self.ui = Ui_rftestui()
        self.ui.setupUi(self)
        self.ui.widlineEdit.setFocus()
        self.initResetDefaultValues()
        self.readCheckBoxHistory()
        self.ui.buttonGoldenSampleConnect.clicked.connect(self.connectToGsStb)
        self.ui.buttonDutConnect.clicked.connect(self.connectToDut)
        self.ui.buttonSave.clicked.connect(self.saveCheckBoxStatus)
        self.ui.widlineEdit.connect(self.ui.widlineEdit, SIGNAL("returnPressed()"), self.readbarcode)
        self.serialObj = 0
        self.msgQ = queue.Queue()
        buildCommandList()

    def readbarcode(self):
        global wid
        str = self.ui.widlineEdit.text()
        if (len(str) != 10):
            print "Fail:", str
            self.ui.widlineEdit.clear()
        else :
            self.ui.buttonDutConnect.setText(str)
            wid = str
            self.ui.widlineEdit.clear()
            self.connectToDut()

    def initResetDefaultValues(self):
        ports = list(port_list.comports())
        for p in ports:
            if(p[2] != 'n/a'):
                self.ui.goldenSampleIfList.addItem(str(p[0]))

        self.ui.dutIpAddressText.setPlainText("192.192.192.2")

    def getcheckboxstatus(self):
        checkboxStatus = ""
        '''if zigbeeTestChannelInfo == "11" :
            checkboxStatus = checkboxStatus + "1"
        elif zigbeeTestChannelInfo == "15" :
            checkboxStatus = checkboxStatus + "2"
        elif zigbeeTestChannelInfo == "20" :
            checkboxStatus = checkboxStatus + "3"
        elif zigbeeTestChannelInfo == "25" :
            checkboxStatus = checkboxStatus + "4"
        else :
            checkboxStatus = checkboxStatus + "0"'''

        if self.ui.checkBoxMSTC.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"
        if self.ui.checkBoxMSTC_UEC_DUMP.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"
        if self.ui.checkBoxUSB.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"
        if self.ui.checkBoxFan.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"
        if self.ui.checkBoxFan_SATA.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"
        if self.ui.checkBoxHDMI.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"
        if self.ui.checkBoxMAC.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"
        if self.ui.checkBoxMOCA.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"
        if self.ui.checkBoxZIGBEE.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"
        if self.ui.checkBoxch11.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"
        if self.ui.checkBoxch15.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"
        if self.ui.checkBoxch20.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"
        if self.ui.checkBoxch25.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"
        if self.ui.checkBoxlnb.isChecked():
            checkboxStatus = checkboxStatus + "1"
        else :
            checkboxStatus = checkboxStatus + "0"


        checkboxStatus = checkboxStatus + "\n"
        checkboxStatus = checkboxStatus + "channelnum=" + zigbeeTestChannelInfo
        return checkboxStatus

    def saveCheckBoxStatus(self):
        file = open("cb.his",'w')
        if (file == 0):
            return
        status = self.getcheckboxstatus()
        file.write(status)
        file.close()

    def readCheckBoxHistory(self):
        if os.path.exists("cb.his") == False :
            return
        # Read checkbox status last use
        file = open("cb.his",'r')
        if (file == 0):
            return
        input = file.readline()
        line = ""
        numofline = 1
        global zigbeeTestChannelInfo
        while input != "" :
            line = line + input
            line = line + " "
            input = file.readline()
            numofline = numofline + 1
        file.close()

        idx = line.find("channelnum=")
        if idx != -1:
            zigbeeTestChannelInfo = line[idx+len("channelnum="):idx+len("channelnum=")+2]
            ch = string.atoi(zigbeeTestChannelInfo, 10)
            if ch > 26 or ch < 11 :
                print "channel num set fail"
                zigbeeTestChannelInfo = "11"

        if len(line) < 13:
            return
        if (line[0] == '1'):
            self.ui.checkBoxMSTC.setChecked(True)
        if (line[1] == '1'):
            self.ui.checkBoxMSTC_UEC_DUMP.setChecked(True)
        if (line[2] == '1'):
            self.ui.checkBoxUSB.setChecked(True)
        if (line[3] == '1'):
            self.ui.checkBoxFan.setChecked(True)
        if (line[4] == '1'):
            self.ui.checkBoxFan_SATA.setChecked(True)
        if (line[5] == '1'):
            self.ui.checkBoxHDMI.setChecked(True)
        if (line[6] == '1'):
            self.ui.checkBoxMAC.setChecked(True)
        if (line[7] == '1'):
            self.ui.checkBoxMOCA.setChecked(True)
        if (line[8] == '1'):
            self.ui.checkBoxZIGBEE.setChecked(True)
        if (line[9] == '1'):
            self.ui.checkBoxch11.setChecked(True)
        if (line[10] == '1'):
            self.ui.checkBoxch15.setChecked(True)
        if (line[11] == '1'):
            self.ui.checkBoxch20.setChecked(True)
        if (line[12] == '1'):
            self.ui.checkBoxch25.setChecked(True)
        if (line[13] == '1'):
            self.ui.checkBoxlnb.setChecked(True)

    '''def disconnectFromDut(self):
        global resultFlag
        self.msgQ.put("closeReportFile")
        time.sleep(1)
        self.telnetObj.telWrite('\x03') #ctrl + c
        time.sleep(1)
        self.telnetObj.telWrite("exit") #Exit
        self.ptcHandlingThread.stopThread()
        self.ui.buttonDutConnect.setEnabled(True)
        self.updateDutConnectionStatus(" Not Connected ")
        resultFlag = True'''


    def connectToGsStb(self):
        print ("Connecting to COM Port  ... ")
        comport = str(self.ui.goldenSampleIfList.currentText())
        if comport == "" :
            self.updateGsConnectionStatus("Not Connected")
            print ("Serial Connection Failed please check the serial port connection")
            return
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

        print (str(self.serialObj))
        print ("connectToGsStb : Connected ")
        self.updateGsConnectionStatus("Connected")
        res = stbPrepareGsRfTest(self,self.serialObj)
        if res != 0:
            self.updateGsConnectionStatus("Not Connected")
            self.serialObj.serExit()
            print ("Serial Connection Failed please check the serial port connection")


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
        self.ui.lnbresult.clear()
        self.ui.lnbresult.hide()
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
        self.ui.dutpowerTestr11result.clear()
        self.ui.dutpowerTestr15result.clear()
        self.ui.dutpowerTestr20result.clear()
        self.ui.dutpowerTestr25result.clear()
        self.ui.powerTestResult_11.clear()
        self.ui.powerTestResult_15.clear()
        self.ui.powerTestResult_20.clear()
        self.ui.powerTestResult_25.clear()
        self.ui.powerTestResult_11.hide()
        self.ui.powerTestResult_15.hide()
        self.ui.powerTestResult_20.hide()
        self.ui.powerTestResult_25.hide()
        self.ui.testEndLabel.clear()
        self.ui.testEndLabel.hide()
        self.ui.rfTestResultValueLabel.clear()
        self.ui.rfTestResultValueLabel.hide()


    def connectToDut(self):
        self.ui.buttonDutConnect.setEnabled(False)
        print ("Check the net enviorment")
        if(test_pingHOST() == 0) :
            self.updateDutConnectionStatus(" Not Connected ")
            self.ui.buttonDutConnect.setEnabled(True)
            return
        print ("Connecting to telnet ... ")
        self.telnetObj = SkedTelnet()
        print ("Connected ")
        self.updateDutConnectionStatus("Connected")
        option = ""
        value = ""
        msg = ""
        if (self.serialObj):
            print("Serial Already open")
        else:
            self.serialObj =1

        self.clearTestResults()
        self.msgQ.put("createReportFile")
        self.ui.widlineEdit.setFocus()
        self.ptcHandlingThread = getPTCThread(self.msgQ,self.telnetObj, self.serialObj, option,value,msg)
        self.connect(self.ptcHandlingThread, SIGNAL("uiUpdateProcess(QString,QString,QString,QString)"),self.uiUpdateProcess)
        self.ptcHandlingThread.start()
        self.ptcHandlingThread.startThread()
        self.checkRfTestItem()

        #self.msgQ.put("startRfTest")
        # auto test enabled
        #self.ptcPerformRfTest()
    def checkRfTestItem(self):
        if self.ui.checkBoxMSTC.isChecked():
            self.msgQ.put("startGetMSTCVersion")
        if self.ui.checkBoxMSTC_UEC_DUMP.isChecked():
            self.msgQ.put("startDumpUECCode")
        if self.ui.checkBoxUSB.isChecked():
            self.msgQ.put("startUSBTest")
        if self.ui.checkBoxFan.isChecked():
            self.msgQ.put("startFANTest")
        if self.ui.checkBoxlnb.isChecked():
            self.msgQ.put("startlnbtest")            
        if self.ui.checkBoxFan_SATA.isChecked():
            self.msgQ.put("startSATATest")
        if self.ui.checkBoxHDMI.isChecked():
            self.msgQ.put("startHDMITest")
        if self.ui.checkBoxMAC.isChecked():
            self.msgQ.put("startMACTest")
        if self.ui.checkBoxMOCA.isChecked():
            self.msgQ.put("startMOCATest")
        if self.ui.checkBoxZIGBEE.isChecked():
            self.msgQ.put("startZIGBEETest")
        if self.ui.checkBoxch11.isChecked():
            self.msgQ.put("startRfPowerTestCh11")
        if self.ui.checkBoxch15.isChecked():
            self.msgQ.put("startRfPowerTestCh15")
        if self.ui.checkBoxch20.isChecked():
            self.msgQ.put("startRfPowerTestCh20")
        if self.ui.checkBoxch25.isChecked():
            self.msgQ.put("startRfPowerTestCh25")
        self.msgQ.put("endTest")

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
        elif(option == "updatePowerLevelResult11"):
            self.updatePowerLevelResult11(result,value)
        elif(option == "updatePowerLevelResult15"):
            self.updatePowerLevelResult15(result,value)
        elif(option == "updatePowerLevelResult20"):
            self.updatePowerLevelResult20(result,value)
        elif(option == "updatePowerLevelResult25"):
            self.updatePowerLevelResult25(result,value)
        elif(option == "updatetestEndLabel"):
            self.updatetestEndLabel(result, value)
        elif(option == "updateTestResult"):
            self.updateTestResult(result, value)
        elif(option == "updateConnectbotton"):
            self.updateConnectbotton(result)
        elif(option == "updateDutConnectionStatus"):
            self.updateDutConnectionStatus(result)
        elif(option == "updatebuttonDutConnect"):
            self.updatebuttonDutConnect(result, value)
        elif(option == "updatelnbtest"):
            self.updatelnbtest(result)

    def updatelnbtest(self, result):
        if result == "1":
            self.ui.lnbresult.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.lnbresult.setText("PASS")
        else :
            self.ui.lnbresult.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.lnbresult.setText("FAIL")
        self.ui.lnbresult.show()

    def updatebuttonDutConnect(self, text, flag):
        self.updatebuttonDutConnect.setText(result)

    def updateConnectbotton(self, value):
        if value == "PASS":
            self.ui.buttonDutConnect.setEnabled(True)
        else:
            self.ui.buttonDutConnect.setEnabled(False)

    def updateGsConnectionStatus(self,text):
        if text == "Connected":
            self.ui.goldenSampleConnectionLabel.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.goldenSampleConnectionLabel.setText("GS Connected")
        else:
            self.ui.goldenSampleConnectionLabel.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
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

    def updatePowerLevelResult11(self,result,text):
        self.ui.powerTestValue.clear()
        self.ui.powerTestValue.setText(text)
        self.ui.powerTestValue.show()
        self.ui.dutpowerTestr11result.clear()
        self.ui.dutpowerTestr11result.setText(text)
        self.ui.dutpowerTestr11result.show()
        if result == "PASS":
            self.ui.powerTestResult_11.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.powerTestResult_11.setText("PASS")
        else:
            self.ui.powerTestResult_11.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.powerTestResult_11.setText("FAIL")
        self.ui.powerTestResult_11.show()

    def updatePowerLevelResult15(self,result,text):
        self.ui.powerTestValue.clear()
        self.ui.powerTestValue.setText(text)
        self.ui.powerTestValue.show()
        self.ui.dutpowerTestr15result.clear()
        self.ui.dutpowerTestr15result.setText(text)
        self.ui.dutpowerTestr15result.show()
        if result == "PASS":
            self.ui.powerTestResult_15.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.powerTestResult_15.setText("PASS")
        else:
            self.ui.powerTestResult_15.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.powerTestResult_15.setText("FAIL")
        self.ui.powerTestResult_15.show()

    def updatePowerLevelResult20(self,result,text):
        self.ui.powerTestValue.clear()
        self.ui.powerTestValue.setText(text)
        self.ui.powerTestValue.show()
        self.ui.dutpowerTestr20result.clear()
        self.ui.dutpowerTestr20result.setText(text)
        self.ui.dutpowerTestr20result.show()
        if result == "PASS":
            self.ui.powerTestResult_20.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.powerTestResult_20.setText("PASS")
        else:
            self.ui.powerTestResult_20.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.powerTestResult_20.setText("FAIL")
        self.ui.powerTestResult_20.show()

    def updatePowerLevelResult25(self,result,text):
        self.ui.powerTestValue.clear()
        self.ui.powerTestValue.setText(text)
        self.ui.powerTestValue.show()
        self.ui.dutpowerTestr25result.clear()
        self.ui.dutpowerTestr25result.setText(text)
        self.ui.dutpowerTestr25result.show()
        if result == "PASS":
            self.ui.powerTestResult_25.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.powerTestResult_25.setText("PASS")
        else:
            self.ui.powerTestResult_25.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.powerTestResult_25.setText("FAIL")
        self.ui.powerTestResult_25.show()

    def updateZigBeeResult(self,result,text):
        print (" updateZigBeeResult")
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
        print (" updateZigBeeResult End")

    def updateSerialNumberInfo(self,result,caId,chipNumber):
        self.ui.caStbIdValueLabel.setStyleSheet(_fromUtf8("QLabel { background-color : white; color : green; }"))
        self.ui.caChipNumValueLabel.setStyleSheet(_fromUtf8("QLabel { background-color : white; color : green; }"))
        self.ui.caStbIdValueLabel.setText(caId)
        self.ui.caChipNumValueLabel.setText(chipNumber)

    def updateTestResult(self, result, value):
        if result == "PASS":
            self.ui.rfTestResultValueLabel.setStyleSheet(_fromUtf8("QLabel { background-color : white; color : green; }"))
            self.ui.rfTestResultValueLabel.setText("PASS")
            self.ui.rfTestResultValueLabel.show()
        elif result == "FAIL":
            self.ui.rfTestResultValueLabel.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.rfTestResultValueLabel.setText("FAIL")
            self.ui.rfTestResultValueLabel.show()

    def updateUsbTestProgress(self,text, value):
        self.ui.usbTestProgressBar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("USB Test :")
        self.ui.statusMsgLabel.setText(text)

    def updateFanTestSpeed(self,text):
        self.ui.fanSpeed.setText(text)

    def updateModelName(self, text):
        self.ui.textStbModel.setText(text)

    def updatetestEndLabel(self, result, text):
        if result == "PASS":
            self.ui.testEndLabel.setStyleSheet(_fromUtf8("QLabel { background-color : green; color : white; }"))
            self.ui.testEndLabel.setText("COMPLETE")
            self.ui.testEndLabel.show()
        elif result == "FAIL":
            self.ui.testEndLabel.setStyleSheet(_fromUtf8("QLabel { background-color : red; color : white; }"))
            self.ui.testEndLabel.setText("ERROR")
            self.ui.testEndLabel.show()
    def forceClose(self):
        # Close comport
        self.serialObj.serExit()
        # Close Telnet
        time.sleep(1)
        self.ptcHandlingThread.telnetObj.telWrite('\x03') #ctrl + c
        time.sleep(1)
        self.ptcHandlingThread.telnetObj.telWrite("exit") #Exit


def stbPerformMocaTest(app,tel,ser):
    findstr= "RX THROUGHPUT PASS"
    findstrInit= "Assume 100"
    findstrFail = "Broken pipe"
    respondFound =0
    findstrGsSampleForMocaDown= "MoCA link is down"
    findstrGsSampleForMocaUp= "MoCA link is up"
    tel.telWrite('\x03') #ctrl + c
    time.sleep(.2)
    tel.telWrite(command_list[TestCommnad.MOCA_TEST_CMD1])
    time.sleep(.2)
    data = tel.telReadSocket(app)
    dataSerial = ser.serRead(app)
    print dataSerial
    tel.telWrite(command_list[TestCommnad.MOCA_TEST_CMD2])
    time.sleep(2)
    dataSerial = ser.serRead(app)
    print dataSerial
    matchDown = re.search(findstrGsSampleForMocaDown,dataSerial)
    matchUp = re.search(findstrGsSampleForMocaUp,dataSerial)
    data = tel.telReadSocket(app)
    print data
    if matchUp:
        print("Mocalink is Up continue the test")
        respondFound =1
    else:# Golden Sample MocaLink is Down-So,Init the moca again to make up
        tel.telWrite(command_list[TestCommnad.MOCA_TEST_CMD2])
        retrycnt = 0
        respondFound = 0
        while retrycnt < 15 and respondFound == 0:
            time.sleep(1)
            dataSerial = ser.serRead(app)
            print dataSerial
            matchUp = re.search(findstrGsSampleForMocaUp,dataSerial)
            if matchUp :
                respondFound = 1
            else :
                retrycnt +=1

    if respondFound == 1 :
        print ("MOCA Init Done ")
    else :
        print ("MOCA FAIL when Init")
        return ''

    #data = tel.telReadSocket(app)
    #print ("going to wait for 15 secs to complete the THROUGHPUT test ")
    retrycnt = 0
    respondFound = 0
    tel.telWrite(command_list[TestCommnad.MOCA_TEST_CMD3])
    while retrycnt < 15 and respondFound == 0:
        time.sleep(1)
        print retrycnt
        data = tel.telReadSocket(app)
        match = re.search(findstr,data)
        matchFail = re.search(findstrFail,data)
        if match :
            respondFound = 1
        elif matchFail:
            print ("MOCA FAIL")
            return ''
        else :
            retrycnt +=1
    if respondFound == 1 :
        print ("MOCA PASS ")
        return data
    else :
        print ("MOCA FAIL")
        return ''

def stbPerformZigBeeTest(app,tel,ser):
    findstr= "Avg RSSI"
    findstrInit = "PAN"
    findstrChSet = "Channel set to "
    findstrAnSet = "Selected Antenna"
    findstrTxPwrSet = "Set TX Power to"
    findstrTxTransmission = "Start Transmission"
    findstrTxTransmissionDone = "Packets sent successfully"


    respondFound = 0
    # Type the following commands in DUT
    #GP510GP510_transceiver 2
    # ch 20
    # an 0
    # R
    # rx 1

    #Setup DUT for Zigbee test
    print (" Setup DUT for Zigbee Test, use channel:")
    print [zigbeeTestChannelInfo]
    tel.telWrite('\x03') #ctrl + c
    time.sleep(.2)
    tel.telWrite("GP510_transceiver 2")
    time.sleep(2)
    data = tel.telReadSocket(app)
    match = re.search(findstrInit,data)
    if match:
        #Init done
        cmd = "ch " + zigbeeTestChannelInfo
        tel.telWrite(cmd)
        time.sleep(.2)
        data = tel.telReadSocket(app)

        #Channel Set OK
        tel.telWrite("an 0")
        time.sleep(.2)
        data = tel.telReadSocket(app)

        tel.telWrite("R") # Reset RX and TX counters
        time.sleep(.2)
        data = tel.telReadSocket(app)

        tel.telWrite("rx 1") # Enable Receiver rx 1
        time.sleep(.2)
        data = tel.telReadSocket(app)
        # Grover add for communication issue
        # Dut always slow one command
        # add this to enable rx temply
        # This is not a solution
        tel.telWrite(cmd)
        time.sleep(.2)
        data = tel.telReadSocket(app)

    #golden sample setup
    print ("Golden Sample Setup start ")
    try:
        ser.serWrite('\x03') #ctrl + c
    except:
        time.sleep(1)
        print (" Return msg 2")
        return ''

    #send the Command to Golden Sample
    ser.serWrite('\x03') #ctrl + c
    time.sleep(.2)
    ser.serWrite("GP510_transceiver 2")
    time.sleep(2)
    data = ser.serRead(app)
    match = re.search(findstrInit,data)
    if match:
        print ("GS: GP510_transceiver data Found ")
        respondFound = 1
        retrycnt = 0
    else:
        respondFound = 0
        retrycnt = 0
        while retrycnt < 15 and respondFound == 0:
            time.sleep(1)
            data = ser.serRead(app)
            match = re.search(findstrInit,data)
            if match :
                print ("GS: GP510_transceiver data Found ")
                respondFound = 1
            else :
                print ("GS: Not Found Retry")
                retrycnt +=1

    if respondFound:
        print("GS Init Done Start sending commands")
        #Init done
        ser.serWrite(cmd)
        time.sleep(.2)
        ser.serWrite("\r\n")
        data = ser.serRead(app)
        print("GS Ch Set ")
        print ([data])
        match = re.search(findstrChSet,data)
        if match:
            print ("GS: Channel set Found ")
            respondFound = 1
            retrycnt = 0
        else:
            respondFound = 0
            retrycnt = 0
            while retrycnt < 15 and respondFound == 0:
                time.sleep(1)
                data = ser.serRead(app)
                match = re.search(findstrChSet,data)
                if match :
                    print ("GS: Channel set Found ")
                    respondFound = 1
                else :
                    print ("GS: Channel set Not Found Retry")
                    retrycnt +=1

        #Channel Set OK
        ser.serWrite("an 0")
        time.sleep(.2)
        ser.serWrite("\r\n")
        data = ser.serRead(app)
        print("GS Ant Set ")
        match = re.search(findstrAnSet,data)
        if match:
            print ("GS: Antenna set Found ")
            respondFound = 1
            retrycnt = 0
        else:
            respondFound = 0
            retrycnt = 0
            while retrycnt < 15 and respondFound == 0:
                time.sleep(1)
                data = ser.serRead(app)
                match = re.search(findstrAnSet,data)
                if match :
                    print ("GS: Antenna set Found ")
                    respondFound = 1
                else :
                    print ("GS: Antenna set Not Found Retry")
                    retrycnt +=1

        ser.serWrite("w 3") # set TX Power
        time.sleep(.2)
        ser.serWrite("\r\n")
        data = ser.serRead(app)
        match = re.search(findstrTxPwrSet,data)
        if match:
            print ("GS: Tx power set Found ")
            respondFound = 1
            retrycnt = 0
        else:
            respondFound = 0
            retrycnt = 0
            while retrycnt < 15 and respondFound == 0:
                time.sleep(1)
                data = ser.serRead(app)
                match = re.search(findstrTxPwrSet,data)
                if match :
                    print ("GS: Tx power set Found ")
                    respondFound = 1
                else :
                    print ("GS: Tx Power set Not Found Retry")
                    retrycnt +=1

        print("GS TX Power Set ")
        print (" Start sending 1000 packets every 10 ms")
        ser.serWrite("tx 1000 10")
        time.sleep(.2)
        ser.serWrite("\r\n")
        data = ser.serRead(app)
        match = re.search(findstrTxTransmission,data)
        if match:
            print ("GS:Tx transmission Found ")
            respondFound = 1
            retrycnt = 0
        else:
            respondFound = 0
            retrycnt = 0
            while retrycnt < 15 and respondFound == 0:
                time.sleep(1)
                data = ser.serRead(app)
                match = re.search(findstrTxTransmission,data)
                if match :
                    print ("GS: Tx transmission set Found ")
                    respondFound = 1
                else :
                    print ("GS: Tx transmission set Not Found Retry")
                    retrycnt +=1



        data = ser.serRead(app)
        match = re.search(findstrTxTransmissionDone,data)
        if match:
            print ("GS:Tx transmission Found ")
            respondFound = 1
            retrycnt = 0
        else:
            respondFound = 0
            retrycnt = 0
            while retrycnt < 15 and respondFound == 0:
                time.sleep(1)
                data = ser.serRead(app)
                match = re.search(findstrTxTransmissionDone,data)
                if match :
                    print ("GS: Tx transmission set Found ")
                    respondFound = 1
                else :
                    print ("GS: Tx transmission set Not Found Retry")
                    retrycnt +=1
        print ("DUT Setup Done ")

        retrycnt = 0
        respondFound = 0
        while retrycnt < 15 and respondFound == 0:
            tel.telWrite("P")
            time.sleep(1)
            data = tel.telReadSocket(app)
            match = re.search(findstr,data)
            if match :
                print ("ZigBee PASS ")
                respondFound = 1
            else :
                retrycnt +=1

    if respondFound :
        print ("ZigBee PASS ")
    else :
        print ("ZigBee FAIL")

    tel.telWrite("rx 0")
    time.sleep(.2)
    ser.serWrite("\r\n")
    tel.telWrite('\x03') #ctrl + c
    time.sleep(.2)
    ser.serWrite('\x03') #ctrl + c
    time.sleep(.2)
    value = data.split('\n')
    for i in value:
        print ([i])

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
        print (" Return msg 2")
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
def stbPerformLNBTest(app, tel, ser):
    currentProgressbarValue = 20
    matchStr18V = "18V"
    matchStr22k ="22k:on"
    print "LNB 18V ON and 22Khz ON"
    tel.telWrite("diseqc 18 1")
    time.sleep(1)
    data = tel.telReadSocket(app)
    match = re.search(matchStr18V,data)
    match1 = re.search(matchStr22k,data)
    if match and match1:
        return 1
    else:
        return 0

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
        print ([data])
        if match:
            #Init done
            respondFound = 0
            retrycnt = 0
            while retrycnt < 15 and respondFound == 0:
                tel.telWrite(command_list[TestCommnad.RF_ANT_SEL_CMD])
                time.sleep(1)
                data = tel.telReadSocket(app)
                print ([data])
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
            print ([data])
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
        print ([data])
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
        print ([data])
        match = re.search(findCwustr,data)
        if match :
            respondFound = 1
        else :
            retrycnt +=1

    data = re.sub('\W+','', data)
    if data == '':
        return data

    path = "Release\SignalHoundSKT.exe ch" + str(chnum)
    print "Run  SignalHoundSKT:", path
    result = os.system(path)
    if result == 1:
        print("File open failed")
        return ''
    path = "powerLevel.txt"
    fp = open(path, "r")
    line = ""
    line = fp.readline()
    if line == "\n":
        line = fp.readline()

    fp.close()
    return re.sub('\s+', '', line)

def stbStopChannelPowerTesting(app,tel,ser):
    findWaveDisableStr = "Continuous Wave Disabled"
    # Disable the Continuous Wave
    respondFound = 0
    retrycnt = 0
    while retrycnt < 15 and respondFound == 0:
        tel.telWrite(command_list[TestCommnad.DUT_CH_PWR_TEST_STOP_CMD])
        time.sleep(1)
        data = tel.telReadSocket(app)
        print ([data])
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
    data = ser.serRead(app)
    match = re.search(statusStr,data)
    if match :
        waitforfind = 0
        print (data)
    else:
        waitforfind = 1
        retryCnt = 0
        while waitforfind and retryCnt < 5:
            data = ser.serRead(app)
            print (data)
            time.sleep(2)
            match = re.search(statusStr,data)
            if match :
                waitforfind = 0
                print (data)
            else:
                print ("Read Fail Retry ")
                print (retryCnt)
                retryCnt +=1

    if waitforfind != 0 :
        return 1;
    #Config the network
    write_cmd = "ifconfig eth0 192.192.192.1"
    ser.serWrite(write_cmd)
    time.sleep(.2)
    data = ser.serRead(app)
    print (data)
    write_cmd = "ifconfig eth1 192.192.168.1"
    ser.serWrite(write_cmd)
    time.sleep(.2)
    data = ser.serRead(app)
    print (data)

    write_cmd = "/root/bin/init_moca"
    ser.serWrite(write_cmd)
    time.sleep(1)
    data = ser.serRead(app)
    print (data)

    write_cmd = "iperf -s &"
    ser.serWrite(write_cmd)
    time.sleep(1)
    data = ser.serRead(app)
    print (data)

    write_cmd = "pstree"
    ser.serWrite(write_cmd)
    time.sleep(1)
    data = ser.serRead(app)
    print (data)

    return 0;

def stbProgramMacAddress( app, tel) :
    statusStr = "Write MAC successfully"

    tel.telWrite('\x03') #ctrl + c
    time.sleep(.2)
    write_cmd = command_list[TestCommnad.WRITE_MAC] + " "+"001222FFFFF0"
    tel.telWrite(write_cmd)
    time.sleep(.2)
    print (time.time())
    waitforfind = 1
    while waitforfind:
        data = tel.telReadSocket(app)
        match = re.search(statusStr,data)
        if match :
            waitforfind = 0
            print (data)
            macadd = stbGetMacAddress(app,tel)
            return macadd[0]
        else:
            continue

def stbGetSoftwareVersion( app, tel) :
    tel.telWrite(command_list[TestCommnad.GET_VER])
    time.sleep(.2)
    data = tel.telReadSocket(app)
    print ([data])
    swver = data[(data.find("stb")):]
    print ([swver])
    swver =  swver.translate(None,'#')
    swver = swver[:-3]
    #swver = re.sub('\W+','', swver)
    #
    print ([swver])
    return swver

def stbDumpUecCode(app,tel) :
    dumpResponseString = "seconds"
    dumpMd5SumString = "UECN1_nopad_dump"
    tel.telWrite(command_list[TestCommnad.DUMP_UECCODE])
    data = tel.telReadSocket(app)
    print (data)
    waitforfind = 1
    while waitforfind:
        data = tel.telReadSocket(app)
        match = re.search(dumpResponseString,data)
        if match :
            waitforfind = 0
            print (data)
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
            print ([data1])
            data1 = re.sub('/tmp/UECN1_nopad_dump','', data1)
            print ([data1])
            data1 = re.sub('\W+','', data1)
            print ([data1])
            data1 = re.sub('md5sumtmpUECN1','', data1)
            print ([data1])
            return data1
        else:
            continue

def stbGetSerialNumber(app, tel):
    snInfo = []
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
            print ([data])

        stbid = (data[0:16])
        print ([stbid])
        chipNum = (data[16:24])
        print ([chipNum])
        snInfo = [stbid, chipNum]
    return snInfo



def stbGetMacAddress( app, tel) :
    macaddrFindString = ":"
    tel.telWrite(command_list[TestCommnad.GET_MACADR])
    time.sleep(.2)
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
                print (list(ethmac))
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
    time.sleep(1)
    tel.telWrite(command_list[TestCommnad.FAN_TEST_CMD5])
    time.sleep(1)
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
        print (" Fan Module Not Removed ")
    else :
        print (" Fan Module Removed ")


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
    time.sleep(1)
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
    data = tel.telReadSocket(app)
    return "Check Video"

def stbPerformHddTest(app,tel):
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    hddTestCompleteString = "aft"
    hddTestFailString = "Sata'test is failed"

    tel.telWrite(command_list[TestCommnad.HDD_TEST])
    HddTestStartedFlag = 1

    print ("Test is Progress")
    while HddTestStartedFlag: # keep read the socket untill get pass result
        data = tel.telReadSocket(app)
        match1 = re.search(hddTestCompleteString,data)
        match2 = re.search(hddTestFailString,data)
        if match1 or match2:
            print ("HDD test Completed")
            HddTestStartedFlag = 0
            if match2:
                print ("HDD Test Failed")
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
    print ("App Closed force")
    exitFlag = 1

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = SkedYesUI()
    myapp.setWindowTitle(_translate("RFTEST", "SKED YES V1.19", None))
    myapp.show()
    QtCore.QObject.connect(app, QtCore.SIGNAL(_fromUtf8("lastWindowClosed()")),forceCloseApp)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())
