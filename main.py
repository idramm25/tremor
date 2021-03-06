# starting sudo from venv for port access:
# sudo -E env PATH=$PATH python main.py
import sys
from datetime import date
from PyQt5 import QtWidgets, uic
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice, QDate
import pyqtgraph as pg
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QWidget
# from saveFileDialog import app

import json
import csv

app = QtWidgets.QApplication([])
ui = uic.loadUi("design.ui")
ui.setWindowTitle("Tremorograph ADXL345 v1.0")
# ---------------------------------------------


serial = QSerialPort()
serial.setBaudRate(115200)
serial.setReadBufferSize(0)
portList = []
speedList = ["6", "25", "50", "100", "200", "400"]
gravityList = ["2", "4", "8", "16"]
ports = QSerialPortInfo.availablePorts()
for port in ports:
    portList.append(port.portName())
ui.comL.addItems(portList)
ui.speedRate.addItems(speedList)
ui.gravityRange.addItems(gravityList)

duration = 0
countR = 0
drate = 0
listX = []
listY = []
listY1 = []
listY2 = []
measuringRight = []
measuringLeft = []


def onRead():
    global measuringRight
    global measuringLeft
    rl = 0
    global countR
    global listX
    global listY
    global listY1
    global listY2
    if serial.canReadLine():
        j = json.loads(str(serial.readLine(), 'utf-8'))
        if "rate" not in j and ui.tabRight.isVisible():
            rl = 1
            measuringRight.append(j)
        elif "rate" not in j and ui.tabLeft.isVisible():
            rl = 2
            measuringLeft.append(j)
        # elif "rate" not in j and ui.tabTable.isVisible():
        #     showCriticalDialog()
        #     serial.flush()
        #     return
        #     # dlg = CustomDialog()
        # dlg.exec()

        if "led" in j:
            ui.term.appendPlainText(str(j['led']))
        elif "rate" in j:
            ui.term.appendPlainText(str(j['rate']))
        elif "count" in j:
            c = j['count']
            x = j['x']
            y = j['y']
            z = j['z']
            countR = c
            listY = listY[1:]
            listY1 = listY1[1:]
            listY2 = listY2[1:]
            listY.append(x)
            listY1.append(y)
            listY2.append(z)
            # ui.graph.clear()
            # ui.graph.plot(listX, listY1)
            # ui.graph.plot(listX, listY1)
            # ui.graph.plot(listX, listY2)
            setProgBar(c)
            ui.term.appendPlainText("count: " + str(c) + "x: " + str(x) + "y: " + str(y) + "z: " + str(z))
        elif "manualstop" in j:
            ui.term.appendPlainText("Manual stop")
    if countR == 0:
        drawGraph(rl)


# def saveFileDialog():
#     options = QFileDialog.Options()
#     options |= QFileDialog.DontUseNativeDialog
#     name, _ = QFileDialog.getSaveFileName(None,
#                                           "", "CSV Files (*.csv);;All Files (*)",
#                                           options=options)
#     file = open(name, 'w')
#     # text = self.textEdit.toPlainText()
#     text = "hello"
#     file.write(text)
#     file.close()


class SaveFile(QWidget):

    def __init__(self):
        super().__init__(self)
        self.title = 'PyQt5 file dialogs - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # self.openFileNameDialog()
        # self.openFileNamesDialog()
        # self.saveFileDialog()
        self.file_save()
        # self.show()

    def file_save(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        name, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "", "CSV Files (*.csv);;All Files (*)", options=options)
        file = open(name,'w')
        # text = self.textEdit.toPlainText()
        text = "hello"
        file.write(text)
        file.close()

def showCriticalDialog(msg):
    msg = msg
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Critical)
    msgBox.setText(msg)
    msgBox.setWindowTitle("Error")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()
    # msgBox.buttonClicked.connect(msgButtonClick)
    # returnValue = msgBox.exec()
    # if returnValue == QMessageBox.Ok:
    #     print('OK clicked')


def showInfoDialog(msg):
    msg = msg
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(msg)
    msgBox.setWindowTitle("Information")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


def msgButtonClick(i):
    print("Button clicked is:", i.text())


def writeCSVRight():
    # name = QFileDialog.getSaveFileName(self,'Save File')
    # file = open(name,'w')
    # # text = textEdit.toPlainText()
    # file.write(text)
    # file.close()
    print("right")


def writeCSVLeft():
    print("left")
    # Python program to convert
    # JSON file to CSV
    # Opening JSON file and loading the data
    # into the variable data
    # with open('data.json') as json_file:
    #     data = json.load(json_file)
    #
    # employee_data = data['emp_details']
    #
    # # now we will open a file for writing
    # data_file = open('data_file.csv', 'w')
    #
    # # create the csv writer object
    # csv_writer = csv.writer(data_file)
    #
    # # Counter variable used for writing
    # # headers to the CSV file
    # count = 0
    #
    # for emp in employee_data:
    #     if count == 0:
    #         # Writing headers of CSV file
    #         header = emp.keys()
    #         csv_writer.writerow(header)
    #         count += 1
    #
    #     # Writing data of CSV file
    #     csv_writer.writerow(emp.values())
    #
    # data_file.close()


# -------------------------------------------------------------------------

# class CustomDialog(QDialog):  # https://www.pythonguis.com/tutorials/pyqt-dialogs/
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#         self.setWindowTitle("HELLO!")
#
#         QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
#
#         self.buttonBox = QDialogButtonBox(QBtn)
#         self.buttonBox.accepted.connect(self.accept)
#         self.buttonBox.rejected.connect(self.reject)
#
#         self.layout = QVBoxLayout()
#         message = QLabel("Something happened, is that OK?")
#         self.layout.addWidget(message)
#         self.layout.addWidget(self.buttonBox)
#         self.setLayout(self.layout)


# def file_save(self):
#     name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
#     file = open(name, 'w')
#     text = self.textEdit.toPlainText()
#     file.write(text)
#     file.close()


def drawGraph(i):
    global listX
    global listY1
    if i == 1:
        ui.graphRight.clear()
        ui.graphRight.plot(listX, listY1)
    elif i == 2:
        ui.graphLeft.clear()
        ui.graphLeft.plot(listX, listY1)


def getMaxCount():
    max_count = int(ui.dur.value()) * int(ui.speedRate.currentText())
    return max_count


def setProgBar(c):
    count = c
    max_count = int(ui.dur.value()) * int(ui.speedRate.currentText())
    i = 100 * (max_count - count) / max_count
    ui.progressBar.setValue(int(i))


def onOpen():
    serial.setPortName(ui.comL.currentText())
    serial.open(QIODevice.ReadWrite)
    print("opened " + serial.portName())


def serialSend(data):  # int list
    # print(data)
    # if serial.isOpen():
    serial.write(json.dumps(data).encode())
    serial.flush()


def onClose():
    serial.close()
    print("closed " + serial.portName())


def sendSettings():  # setup string to device {"g-range":2,"d-rate":100}
    if serial.isOpen():
        grange = ui.gravityRange.currentText()
        global drate
        drate = ui.speedRate.currentText()
        s = {
            "g-range": str(grange),
            "d-rate": float(drate)
        }
        serialSend(s)
    else:
        showCriticalDialog(msg="Device port is not open")


def startMeasuring():
    if serial.isOpen():
        if not ui.tabTable.isVisible():
            global duration
            duration = ui.dur.value()  # string for start: {"start":10} \\\10 sec
            s = {
                "start": str(duration)
            }
            c = getMaxCount()
            global listX
            global listY
            del listX[:]
            del listY1[:]
            for x in range(c):
                listX.append(x)
            for y in range(c):
                listY1.append(0)
            serialSend(s)
        else:
            showCriticalDialog(msg='Chose "Graph right" or "Graph left" for measuring')
            # return
    else:
        showCriticalDialog(msg='Device port is not opened yet. Press "Open port" for continue')


def stopMeasuring():  # string for stop: {"stop":1}
    if serial.isOpen():
        if not ui.tabTable.isVisible():
            s = {
                "stop": 1
            }
            serialSend(s)
        else:
            showCriticalDialog()
    else:
        showCriticalDialog(msg='Device port is not opened yet. Press "Open port" for continue')


def setProgVal():
    ui.progLabel.setText(str(int(ui.dur.value()) * int(ui.speedRate.currentText())))


def graphRightClear():
    global listX
    global listY
    del listX[:]
    del listY[:]
    ui.graphRight.clear()


def graphLeftClear():
    global listX
    global listY
    del listX[:]
    del listY[:]
    ui.graphLeft.clear()


def newWinPlot():
    global listX
    global listY
    if listX and listY:
        pg.plot(listX, listY1)
    else:
        showInfoDialog(msg="Start measuring first!")


def loadTableDataRight():
    global measuringRight
    if measuringRight:
        if measuringRight:
            row = 0
            ui.rightTable.setRowCount(len(measuringRight))
            for measure in measuringRight:
                ui.rightTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(measure["count"])))
                ui.rightTable.setItem(row, 1, QtWidgets.QTableWidgetItem(str(measure["x"])))
                ui.rightTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(measure["y"])))
                ui.rightTable.setItem(row, 3, QtWidgets.QTableWidgetItem(str(measure["z"])))
                row = row + 1
    else:
        showInfoDialog(msg="Start measuring first!")


def loadTableDataLeft():
    global measuringLeft
    if measuringLeft:
        if measuringLeft:
            row = 0
            ui.leftTable.setRowCount(len(measuringLeft))
            for measure in measuringLeft:
                ui.leftTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(measure["count"])))
                ui.leftTable.setItem(row, 1, QtWidgets.QTableWidgetItem(str(measure["x"])))
                ui.leftTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(measure["y"])))
                ui.leftTable.setItem(row, 3, QtWidgets.QTableWidgetItem(str(measure["z"])))
                row = row + 1
    else:
        showInfoDialog(msg="Start measuring first!")


def led():
    s = {
        "led": 1
    }
    serialSend(s)


def clearRightTab():
    ui.rightTable.setRowCount(0)


def clearLeftTab():
    ui.leftTable.setRowCount(0)


ui.speedRate.currentIndexChanged.connect(setProgVal)
ui.dur.valueChanged.connect(setProgVal)

serial.readyRead.connect(onRead)
# ------BUTTONS--------------------
ui.openB.clicked.connect(onOpen)
ui.closeB.clicked.connect(onClose)
ui.setB.clicked.connect(sendSettings)
ui.startB.clicked.connect(startMeasuring)
ui.stopB.clicked.connect(stopMeasuring)
ui.ledButton.clicked.connect(led)
ui.clearBR.clicked.connect(graphRightClear)
ui.clearBL.clicked.connect(graphLeftClear)
ui.newWR.clicked.connect(newWinPlot)
ui.newWL.clicked.connect(newWinPlot)
ui.fillTR.clicked.connect(loadTableDataRight)
ui.fillTL.clicked.connect(loadTableDataLeft)
ui.clearTabRight.clicked.connect(clearRightTab)
ui.clearTabLeft.clicked.connect(clearLeftTab)
ui.saveCSVLeft.clicked.connect(writeCSVLeft)
ui.saveCSVRight.clicked.connect(writeCSVRight)
# -------------------------------------------

ui.dateEdit.setDate(QDate(date.today()))

ui.progLabel.setText(str(int(ui.dur.value()) * int(ui.speedRate.currentText())))
ui.progressBar.setValue(0)

ui.show()
sys.exit(app.exec())
