# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rftest.ui'
#
# Created by: PyQt4 UI code generator 4.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_rftestui(object):
    def setupUi(self, rftestui):
        rftestui.setObjectName(_fromUtf8("rftestui"))
        rftestui.resize(640, 479)
        self.buttonDutDisconnect = QtGui.QPushButton(rftestui)
        self.buttonDutDisconnect.setGeometry(QtCore.QRect(330, 40, 72, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.buttonDutDisconnect.setFont(font)
        self.buttonDutDisconnect.setObjectName(_fromUtf8("buttonDutDisconnect"))
        self.caStbIdValueLabel = QtGui.QLabel(rftestui)
        self.caStbIdValueLabel.setGeometry(QtCore.QRect(480, 80, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.caStbIdValueLabel.setFont(font)
        self.caStbIdValueLabel.setObjectName(_fromUtf8("caStbIdValueLabel"))
        self.sataResult = QtGui.QLabel(rftestui)
        self.sataResult.setGeometry(QtCore.QRect(310, 184, 48, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.sataResult.setFont(font)
        self.sataResult.setText(_fromUtf8(""))
        self.sataResult.setObjectName(_fromUtf8("sataResult"))
        self.line_2 = QtGui.QFrame(rftestui)
        self.line_2.setGeometry(QtCore.QRect(0, 230, 641, 16))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.rfTestResultValueLabel = QtGui.QLabel(rftestui)
        self.rfTestResultValueLabel.setGeometry(QtCore.QRect(480, 210, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.rfTestResultValueLabel.setFont(font)
        self.rfTestResultValueLabel.setObjectName(_fromUtf8("rfTestResultValueLabel"))
        self.buttonDutConnect = QtGui.QPushButton(rftestui)
        self.buttonDutConnect.setGeometry(QtCore.QRect(250, 40, 72, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.buttonDutConnect.setFont(font)
        self.buttonDutConnect.setObjectName(_fromUtf8("buttonDutConnect"))
        self.fanValue = QtGui.QTextEdit(rftestui)
        self.fanValue.setGeometry(QtCore.QRect(120, 158, 140, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.fanValue.setFont(font)
        self.fanValue.setObjectName(_fromUtf8("fanValue"))
        self.fanLabel = QtGui.QLabel(rftestui)
        self.fanLabel.setGeometry(QtCore.QRect(10, 158, 102, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.fanLabel.setFont(font)
        self.fanLabel.setObjectName(_fromUtf8("fanLabel"))
        self.dutIpAddressText = QtGui.QTextEdit(rftestui)
        self.dutIpAddressText.setGeometry(QtCore.QRect(111, 40, 121, 22))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.dutIpAddressText.setFont(font)
        self.dutIpAddressText.setAutoFormatting(QtGui.QTextEdit.AutoNone)
        self.dutIpAddressText.setObjectName(_fromUtf8("dutIpAddressText"))
        self.sataValue = QtGui.QTextEdit(rftestui)
        self.sataValue.setGeometry(QtCore.QRect(120, 184, 140, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.sataValue.setFont(font)
        self.sataValue.setObjectName(_fromUtf8("sataValue"))
        self.uecCodeDumpLabel = QtGui.QLabel(rftestui)
        self.uecCodeDumpLabel.setGeometry(QtCore.QRect(10, 106, 102, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.uecCodeDumpLabel.setFont(font)
        self.uecCodeDumpLabel.setObjectName(_fromUtf8("uecCodeDumpLabel"))
        self.fanResult = QtGui.QLabel(rftestui)
        self.fanResult.setGeometry(QtCore.QRect(310, 158, 48, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.fanResult.setFont(font)
        self.fanResult.setText(_fromUtf8(""))
        self.fanResult.setObjectName(_fromUtf8("fanResult"))
        self.goldenSampleIfList = QtGui.QComboBox(rftestui)
        self.goldenSampleIfList.setGeometry(QtCore.QRect(160, 10, 72, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.goldenSampleIfList.setFont(font)
        self.goldenSampleIfList.setEditable(True)
        self.goldenSampleIfList.setObjectName(_fromUtf8("goldenSampleIfList"))
        self.versionLabel = QtGui.QLabel(rftestui)
        self.versionLabel.setGeometry(QtCore.QRect(10, 80, 102, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.versionLabel.setFont(font)
        self.versionLabel.setObjectName(_fromUtf8("versionLabel"))
        self.dumpUecCodeValue = QtGui.QTextEdit(rftestui)
        self.dumpUecCodeValue.setGeometry(QtCore.QRect(120, 106, 140, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.dumpUecCodeValue.setFont(font)
        self.dumpUecCodeValue.setObjectName(_fromUtf8("dumpUecCodeValue"))
        self.htpVersionValue = QtGui.QTextEdit(rftestui)
        self.htpVersionValue.setGeometry(QtCore.QRect(120, 80, 140, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.htpVersionValue.setFont(font)
        self.htpVersionValue.setObjectName(_fromUtf8("htpVersionValue"))
        self.buttonExit = QtGui.QPushButton(rftestui)
        self.buttonExit.setGeometry(QtCore.QRect(550, 40, 72, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.buttonExit.setFont(font)
        self.buttonExit.setObjectName(_fromUtf8("buttonExit"))
        self.buttonGoldenSampleConnect = QtGui.QPushButton(rftestui)
        self.buttonGoldenSampleConnect.setGeometry(QtCore.QRect(250, 10, 72, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.buttonGoldenSampleConnect.setFont(font)
        self.buttonGoldenSampleConnect.setObjectName(_fromUtf8("buttonGoldenSampleConnect"))
        self.dutIfLabel = QtGui.QLabel(rftestui)
        self.dutIfLabel.setGeometry(QtCore.QRect(10, 40, 60, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.dutIfLabel.setFont(font)
        self.dutIfLabel.setObjectName(_fromUtf8("dutIfLabel"))
        self.rfTestGroup = QtGui.QGroupBox(rftestui)
        self.rfTestGroup.setGeometry(QtCore.QRect(0, 240, 631, 241))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.rfTestGroup.setFont(font)
        self.rfTestGroup.setObjectName(_fromUtf8("rfTestGroup"))
        self.hdmiLabel_2 = QtGui.QLabel(self.rfTestGroup)
        self.hdmiLabel_2.setGeometry(QtCore.QRect(10, 20, 102, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.hdmiLabel_2.setFont(font)
        self.hdmiLabel_2.setObjectName(_fromUtf8("hdmiLabel_2"))
        self.dutMacAddress = QtGui.QTextEdit(self.rfTestGroup)
        self.dutMacAddress.setGeometry(QtCore.QRect(120, 20, 140, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.dutMacAddress.setFont(font)
        self.dutMacAddress.setObjectName(_fromUtf8("dutMacAddress"))
        self.dutMocaTest = QtGui.QLabel(self.rfTestGroup)
        self.dutMocaTest.setGeometry(QtCore.QRect(10, 50, 102, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.dutMocaTest.setFont(font)
        self.dutMocaTest.setObjectName(_fromUtf8("dutMocaTest"))
        self.dutMocaRestult = QtGui.QTextEdit(self.rfTestGroup)
        self.dutMocaRestult.setGeometry(QtCore.QRect(120, 50, 140, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.dutMocaRestult.setFont(font)
        self.dutMocaRestult.setObjectName(_fromUtf8("dutMocaRestult"))
        self.dutZigBeeTest = QtGui.QLabel(self.rfTestGroup)
        self.dutZigBeeTest.setGeometry(QtCore.QRect(10, 80, 102, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.dutZigBeeTest.setFont(font)
        self.dutZigBeeTest.setObjectName(_fromUtf8("dutZigBeeTest"))
        self.dutZigbeeResult = QtGui.QTextEdit(self.rfTestGroup)
        self.dutZigbeeResult.setGeometry(QtCore.QRect(120, 80, 140, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.dutZigbeeResult.setFont(font)
        self.dutZigbeeResult.setObjectName(_fromUtf8("dutZigbeeResult"))
        self.line_3 = QtGui.QFrame(self.rfTestGroup)
        self.line_3.setGeometry(QtCore.QRect(0, 110, 641, 16))
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.powerTestLabel = QtGui.QLabel(self.rfTestGroup)
        self.powerTestLabel.setGeometry(QtCore.QRect(0, 120, 101, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.powerTestLabel.setFont(font)
        self.powerTestLabel.setObjectName(_fromUtf8("powerTestLabel"))
        self.radioButtonCH11 = QtGui.QRadioButton(self.rfTestGroup)
        self.radioButtonCH11.setGeometry(QtCore.QRect(40, 140, 71, 26))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.radioButtonCH11.setFont(font)
        self.radioButtonCH11.setObjectName(_fromUtf8("radioButtonCH11"))
        self.radioButtonCH25 = QtGui.QRadioButton(self.rfTestGroup)
        self.radioButtonCH25.setGeometry(QtCore.QRect(250, 140, 71, 26))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.radioButtonCH25.setFont(font)
        self.radioButtonCH25.setObjectName(_fromUtf8("radioButtonCH25"))
        self.radioButtonCH20 = QtGui.QRadioButton(self.rfTestGroup)
        self.radioButtonCH20.setGeometry(QtCore.QRect(180, 140, 71, 26))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.radioButtonCH20.setFont(font)
        self.radioButtonCH20.setObjectName(_fromUtf8("radioButtonCH20"))
        self.radioButtonCH15 = QtGui.QRadioButton(self.rfTestGroup)
        self.radioButtonCH15.setGeometry(QtCore.QRect(110, 140, 71, 26))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.radioButtonCH15.setFont(font)
        self.radioButtonCH15.setObjectName(_fromUtf8("radioButtonCH15"))
        self.radioButtonCHStop = QtGui.QRadioButton(self.rfTestGroup)
        self.radioButtonCHStop.setGeometry(QtCore.QRect(320, 140, 71, 26))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.radioButtonCHStop.setFont(font)
        self.radioButtonCHStop.setChecked(True)
        self.radioButtonCHStop.setObjectName(_fromUtf8("radioButtonCHStop"))
        self.rfSoftwareVerLabel = QtGui.QLabel(self.rfTestGroup)
        self.rfSoftwareVerLabel.setGeometry(QtCore.QRect(410, 212, 64, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.rfSoftwareVerLabel.setFont(font)
        self.rfSoftwareVerLabel.setObjectName(_fromUtf8("rfSoftwareVerLabel"))
        self.rfSoftwareVerValueLabel = QtGui.QLabel(self.rfTestGroup)
        self.rfSoftwareVerValueLabel.setGeometry(QtCore.QRect(470, 212, 160, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.rfSoftwareVerValueLabel.setFont(font)
        self.rfSoftwareVerValueLabel.setObjectName(_fromUtf8("rfSoftwareVerValueLabel"))
        self.macResult = QtGui.QLabel(self.rfTestGroup)
        self.macResult.setGeometry(QtCore.QRect(310, 20, 48, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.macResult.setFont(font)
        self.macResult.setText(_fromUtf8(""))
        self.macResult.setObjectName(_fromUtf8("macResult"))
        self.mocaResult = QtGui.QLabel(self.rfTestGroup)
        self.mocaResult.setGeometry(QtCore.QRect(310, 50, 48, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.mocaResult.setFont(font)
        self.mocaResult.setText(_fromUtf8(""))
        self.mocaResult.setObjectName(_fromUtf8("mocaResult"))
        self.zigbeeResult = QtGui.QLabel(self.rfTestGroup)
        self.zigbeeResult.setGeometry(QtCore.QRect(310, 80, 48, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.zigbeeResult.setFont(font)
        self.zigbeeResult.setText(_fromUtf8(""))
        self.zigbeeResult.setObjectName(_fromUtf8("zigbeeResult"))
        self.usbValue = QtGui.QTextEdit(rftestui)
        self.usbValue.setGeometry(QtCore.QRect(120, 132, 140, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.usbValue.setFont(font)
        self.usbValue.setObjectName(_fromUtf8("usbValue"))
        self.rfTestResultLabel = QtGui.QLabel(rftestui)
        self.rfTestResultLabel.setGeometry(QtCore.QRect(400, 210, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.rfTestResultLabel.setFont(font)
        self.rfTestResultLabel.setObjectName(_fromUtf8("rfTestResultLabel"))
        self.usbLabel = QtGui.QLabel(rftestui)
        self.usbLabel.setGeometry(QtCore.QRect(10, 132, 102, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.usbLabel.setFont(font)
        self.usbLabel.setObjectName(_fromUtf8("usbLabel"))
        self.buttonReset = QtGui.QPushButton(rftestui)
        self.buttonReset.setGeometry(QtCore.QRect(550, 10, 72, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.buttonReset.setFont(font)
        self.buttonReset.setObjectName(_fromUtf8("buttonReset"))
        self.hdmiOutResult = QtGui.QLabel(rftestui)
        self.hdmiOutResult.setGeometry(QtCore.QRect(310, 210, 48, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.hdmiOutResult.setFont(font)
        self.hdmiOutResult.setText(_fromUtf8(""))
        self.hdmiOutResult.setObjectName(_fromUtf8("hdmiOutResult"))
        self.goldenSampleIfLabel = QtGui.QLabel(rftestui)
        self.goldenSampleIfLabel.setGeometry(QtCore.QRect(10, 10, 131, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.goldenSampleIfLabel.setFont(font)
        self.goldenSampleIfLabel.setObjectName(_fromUtf8("goldenSampleIfLabel"))
        self.caStbIdLabel = QtGui.QLabel(rftestui)
        self.caStbIdLabel.setGeometry(QtCore.QRect(400, 80, 65, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.caStbIdLabel.setFont(font)
        self.caStbIdLabel.setObjectName(_fromUtf8("caStbIdLabel"))
        self.caChipNumValueLabel = QtGui.QLabel(rftestui)
        self.caChipNumValueLabel.setGeometry(QtCore.QRect(480, 106, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.caChipNumValueLabel.setFont(font)
        self.caChipNumValueLabel.setObjectName(_fromUtf8("caChipNumValueLabel"))
        self.htpVersionResult = QtGui.QLabel(rftestui)
        self.htpVersionResult.setGeometry(QtCore.QRect(310, 80, 48, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.htpVersionResult.setFont(font)
        self.htpVersionResult.setText(_fromUtf8(""))
        self.htpVersionResult.setObjectName(_fromUtf8("htpVersionResult"))
        self.caChipNumLabel = QtGui.QLabel(rftestui)
        self.caChipNumLabel.setGeometry(QtCore.QRect(400, 106, 65, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.caChipNumLabel.setFont(font)
        self.caChipNumLabel.setObjectName(_fromUtf8("caChipNumLabel"))
        self.hdmiLabel = QtGui.QLabel(rftestui)
        self.hdmiLabel.setGeometry(QtCore.QRect(10, 210, 102, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.hdmiLabel.setFont(font)
        self.hdmiLabel.setObjectName(_fromUtf8("hdmiLabel"))
        self.dumpCodeResult = QtGui.QLabel(rftestui)
        self.dumpCodeResult.setGeometry(QtCore.QRect(310, 106, 48, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.dumpCodeResult.setFont(font)
        self.dumpCodeResult.setText(_fromUtf8(""))
        self.dumpCodeResult.setObjectName(_fromUtf8("dumpCodeResult"))
        self.hdmiValue = QtGui.QTextEdit(rftestui)
        self.hdmiValue.setGeometry(QtCore.QRect(120, 210, 140, 22))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.hdmiValue.setFont(font)
        self.hdmiValue.setObjectName(_fromUtf8("hdmiValue"))
        self.usbResult = QtGui.QLabel(rftestui)
        self.usbResult.setGeometry(QtCore.QRect(310, 132, 48, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.usbResult.setFont(font)
        self.usbResult.setText(_fromUtf8(""))
        self.usbResult.setObjectName(_fromUtf8("usbResult"))
        self.sataLabel = QtGui.QLabel(rftestui)
        self.sataLabel.setGeometry(QtCore.QRect(10, 184, 102, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.sataLabel.setFont(font)
        self.sataLabel.setObjectName(_fromUtf8("sataLabel"))
        self.line = QtGui.QFrame(rftestui)
        self.line.setGeometry(QtCore.QRect(0, 70, 631, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.goldenSampleConnectionLabel = QtGui.QLabel(rftestui)
        self.goldenSampleConnectionLabel.setGeometry(QtCore.QRect(330, 10, 128, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.goldenSampleConnectionLabel.setFont(font)
        self.goldenSampleConnectionLabel.setObjectName(_fromUtf8("goldenSampleConnectionLabel"))
        self.dutConnectionLabel = QtGui.QLabel(rftestui)
        self.dutConnectionLabel.setGeometry(QtCore.QRect(410, 40, 128, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.dutConnectionLabel.setFont(font)
        self.dutConnectionLabel.setObjectName(_fromUtf8("dutConnectionLabel"))

        self.retranslateUi(rftestui)
        self.goldenSampleIfList.setCurrentIndex(-1)
        QtCore.QObject.connect(self.buttonExit, QtCore.SIGNAL(_fromUtf8("clicked()")), rftestui.close)
        QtCore.QMetaObject.connectSlotsByName(rftestui)

    def retranslateUi(self, rftestui):
        rftestui.setWindowTitle(_translate("rftestui", "Form", None))
        self.buttonDutDisconnect.setText(_translate("rftestui", "DU_Disconnect", None))
        self.caStbIdValueLabel.setText(_translate("rftestui", "0000000000000000", None))
        self.rfTestResultValueLabel.setText(_translate("rftestui", " FAIL", None))
        self.buttonDutConnect.setText(_translate("rftestui", "DU_Connect", None))
        self.fanLabel.setText(_translate("rftestui", "FAN", None))
        self.uecCodeDumpLabel.setText(_translate("rftestui", "DUMP UEC CODE", None))
        self.versionLabel.setText(_translate("rftestui", "MSTC HTP Version", None))
        self.buttonExit.setText(_translate("rftestui", "Exit", None))
        self.buttonGoldenSampleConnect.setText(_translate("rftestui", "GS_Connect", None))
        self.dutIfLabel.setText(_translate("rftestui", "DUT IP", None))
        self.rfTestGroup.setTitle(_translate("rftestui", "RF TEST", None))
        self.hdmiLabel_2.setText(_translate("rftestui", "MAC PROGRAM", None))
        self.dutMocaTest.setText(_translate("rftestui", "MOCA TEST", None))
        self.dutZigBeeTest.setText(_translate("rftestui", "ZIGBEE TEST", None))
        self.powerTestLabel.setText(_translate("rftestui", "POWER TEST", None))
        self.radioButtonCH11.setText(_translate("rftestui", "CH 11", None))
        self.radioButtonCH25.setText(_translate("rftestui", "CH 25", None))
        self.radioButtonCH20.setText(_translate("rftestui", "CH 20", None))
        self.radioButtonCH15.setText(_translate("rftestui", "CH 15", None))
        self.radioButtonCHStop.setText(_translate("rftestui", "Stop", None))
        self.rfSoftwareVerLabel.setText(_translate("rftestui", "SW VER:", None))
        self.rfSoftwareVerValueLabel.setText(_translate("rftestui", "SKED V.0.01_20180918", None))
        self.rfTestResultLabel.setText(_translate("rftestui", "TEST RESULT", None))
        self.usbLabel.setText(_translate("rftestui", "USB", None))
        self.buttonReset.setText(_translate("rftestui", "Reset", None))
        self.goldenSampleIfLabel.setText(_translate("rftestui", "GOLDEN SAMPLE IF", None))
        self.caStbIdLabel.setText(_translate("rftestui", "CA STB ID:", None))
        self.caChipNumValueLabel.setText(_translate("rftestui", "00000000", None))
        self.caChipNumLabel.setText(_translate("rftestui", "CHIP NUM", None))
        self.hdmiLabel.setText(_translate("rftestui", "HDMI VOUT", None))
        self.sataLabel.setText(_translate("rftestui", "SATA", None))
        self.goldenSampleConnectionLabel.setText(_translate("rftestui", "GS Not Connected", None))
        self.dutConnectionLabel.setText(_translate("rftestui", "DUT Not Connected", None))
