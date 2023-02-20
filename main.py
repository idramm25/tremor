# starting sudo from venv for port access:
# sudo -E env PATH=$PATH python main.py
import sys
from datetime import date
from PyQt5 import QtWidgets, uic
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice, QDate
import pyqtgraph as pg
from PyQt5.QtWidgets import QMessageBox, QFileDialog
import json
import csv

app = QtWidgets.QApplication([])
ui = uic.loadUi("design.ui")
ui.setWindowTitle("Tremorograph ADXL345 v1.0")


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
setOk = False
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
        if "led" in j:
            ui.term.appendPlainText("Led " + str(j['led']))
            ui.term.appendPlainText("--------------------------------------")
        elif "rate" in j:
            ui.term.appendPlainText("Rate " + str(j['rate']) + " Hz")
            ui.term.appendPlainText("Range " + ui.gravityRange.currentText() + " G")
            ui.term.appendPlainText("--------------------------------------")
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
            setProgBar(c)
            ui.term.appendPlainText("count: " + str(c) + "x: " + str(x) + "y: " + str(y) + "z: " + str(z))
            if c == 0:
                ui.term.appendPlainText("----------End of data-----------")
        elif "manualstop" in j:
            ui.term.appendPlainText("Manual stop")
            ui.term.appendPlainText("--------------------------------------")
    if countR == 0:
        drawGraph(rl)


def showCriticalDialog(msg):
    msg = msg
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Critical)
    msgBox.setText(msg)
    msgBox.setWindowTitle("Error")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


def showInfoDialog(msg):
    msg = msg
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(msg)
    msgBox.setWindowTitle("Information")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


def save_data_to_csv(measuring_data):
    file_path, _ = QFileDialog.getSaveFileName(None, "Save File", "", "CSV Files (*.csv)")
    if file_path:
        with open(file_path, mode='w', newline='') as file:
            field_names = ['count', 'x', 'y', 'z']
            writer = csv.DictWriter(file, fieldnames=field_names)
            writer.writeheader()
            for row in measuring_data:
                writer.writerow(row)


def writeCSVLeft():
    save_data_to_csv(measuringLeft)


def writeCSVRight():
    save_data_to_csv(measuringRight)


def save_entry_data(patient_name, patient_age, description, date, doctor_name):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filename, _ = QFileDialog.getSaveFileName(None, "Save Data", "", "Text Files (*.txt);;All Files (*)",
                                              options=options)

    if filename:
        with open(filename, 'w') as file:
            file.write(f'Patient Name: {patient_name}\n')
            file.write(f'Patient Age: {patient_age}\n')
            file.write(f'Description: {description}\n')
            file.write(f'Date: {date}\n')
            file.write(f'Doctor Name: {doctor_name}\n')
        print('Data saved successfully')


def create_entry_clicked():
    patient_name = ui.patientName.text()
    patient_age = ui.patientAge.text()
    description = ui.description.toPlainText()
    date = ui.dateEdit.text()
    doctor_name = ui.doctorName.text()
    if patient_name and patient_age and description and doctor_name:
        save_entry_data(patient_name, patient_age, description, date, doctor_name)
    else:
        showCriticalDialog("Some entry field is unfilled")


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



def serialSend(data):  # int list
    serial.write(json.dumps(data).encode())
    serial.flush()


def onOpen():
    serial.setPortName(ui.comL.currentText())
    serial.open(QIODevice.ReadWrite)
    print("opened " + serial.portName())
    ui.term.appendPlainText("Port " + serial.portName() + " opened")
    ui.term.appendPlainText("--------------------------------------")


def onClose():
    global setOk
    serial.close()
    setOk = False
    print("closed " + serial.portName())
    ui.term.appendPlainText("Port " + serial.portName() + " closed")
    ui.term.appendPlainText("--------------------------------------")


def sendSettings():  # setup string to device for example: {"g-range":2,"d-rate":100}
    global setOk
    if serial.isOpen():
        grange = ui.gravityRange.currentText()
        global drate
        drate = ui.speedRate.currentText()
        s = {
            "g-range": str(grange),
            "d-rate": float(drate)
        }
        serialSend(s)
        setOk = True
        ui.term.appendPlainText("Send settings...")
    else:
        showCriticalDialog(msg="Device port is not open")


def startMeasuring():
    global measuringRight
    global measuringLeft
    if setOk:
        if serial.isOpen():
            if not ui.tabTable.isVisible():
                if ui.tabRight.isVisible() and measuringRight:
                    measuringRight.clear()
                elif ui.tabLeft.isVisible() and measuringLeft:
                    measuringLeft.clear()
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
                ui.progressBar.setValue(0)
                ui.term.appendPlainText("Starting measuring")
                ui.term.appendPlainText("--------------------------------------")
                serialSend(s)
            else:
                showCriticalDialog(msg='Chose "Graph right" or "Graph left" for measuring')
        else:
            showCriticalDialog(msg='Device port is not opened yet. Press "Open port" for continue')
    else:
        showCriticalDialog(msg='Please set the measuring speed and gravity range first')


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
    global measuringRight
    measuringRight.clear()


def graphLeftClear():
    global listX
    global listY
    del listX[:]
    del listY[:]
    ui.graphLeft.clear()
    global measuringLeft
    measuringLeft.clear()


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
        ui.term.appendPlainText("Right table filled ok")
        ui.term.appendPlainText("--------------------------------------")
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
        ui.term.appendPlainText("Left table filled ok")
        ui.term.appendPlainText("--------------------------------------")
    else:
        showInfoDialog(msg="Start measuring first!")


def led():
    if serial.isOpen():
        s = {
            "led": 1
        }
        serialSend(s)
    else:
        showCriticalDialog(msg='Device port is not opened yet. Press "Open port" for continue')


def clearRightTab():
    ui.rightTable.setRowCount(0)
    global measuringRight
    measuringRight.clear()


def clearLeftTab():
    ui.leftTable.setRowCount(0)
    global measuringLeft
    measuringLeft.clear()


###########################################################

###########################################################
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
ui.createEntryButton.clicked.connect(create_entry_clicked)
# -------------------------------------------
ui.dateEdit.setDate(QDate(date.today()))
ui.progLabel.setText(str(int(ui.dur.value()) * int(ui.speedRate.currentText())))
ui.progressBar.setValue(0)
ui.show()
sys.exit(app.exec())
