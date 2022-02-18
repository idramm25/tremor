# starting sudo from venv for port access:
# sudo -E env PATH=$PATH python main.py
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice
import json
from pyqtgraph import PlotWidget
import pyqtgraph as pg


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


listX = []
# for x in range(100): listX.append(x)
listY = []
# for y in range(100): listY.append(0)
listY1 = []
listY2 = []

def onRead():
    if serial.canReadLine():
        j = json.loads(str(serial.readLine(), 'utf-8'))
        if "led" in j:
            ui.term.appendPlainText(str(j['led']))
        elif "rate" in j:
            ui.term.appendPlainText(str(j['rate']))
        elif "count" in j:
            c = j['count']
            x = j['x']
            y = j['y']
            z = j['z']
            global listX
            global listY
            global listY1
            global listY2
            listY = listY[1:]
            listY1 = listY1[1:]
            listY2 = listY2[1:]
            listY.append(x)
            listY1.append(y)
            listY2.append(z)
            ui.graph.clear()
            ui.graph.plot(listX, listY)
            # ui.graph.plot(listX, listY1)
            # ui.graph.plot(listX, listY2)
            setProgBar(c)
            ui.term.appendPlainText("count: " + str(c) + "x: " + str(x) + "y: " + str(y) + "z: " + str(z))
        elif "manualstop" in j:
            ui.term.appendPlainText("Manual stop")


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
    grange = ui.gravityRange.currentText()
    global drate
    drate = ui.speedRate.currentText()
    s = {
        "g-range": str(grange),
        "d-rate": float(drate)
    }
    serialSend(s)



def startMeasuring():
    global duration
    duration = ui.dur.value()  # string for start: {"start":10} \\\10 sec
    s = {
        "start": str(duration)
    }
    c = getMaxCount()
    global listX
    global listY
    del listX[:]
    del listY[:]
    for x in range(c): listX.append(x)
    for y in range(c): listY.append(0)
    serialSend(s)


def stopMeasuring():  # string for stop: {"stop":1}
    s = {
        "stop": 1
    }
    serialSend(s)


def led():
    s = {
        "led": 1
    }
    serialSend(s)


def setProgVal():
    ui.progLabel.setText(str(int(ui.dur.value()) * int(ui.speedRate.currentText())))


def graphClear():
    global listX
    global listY
    del listX[:]
    del listY[:]
    ui.graph.clear()


def newWinPlot():
    global listX
    global listY
    pg.plot(listX, listY)

ui.speedRate.currentIndexChanged.connect(setProgVal)
ui.dur.valueChanged.connect(setProgVal)

serial.readyRead.connect(onRead)
ui.openB.clicked.connect(onOpen)
ui.closeB.clicked.connect(onClose)
# ------------------------------------
ui.setB.clicked.connect(sendSettings)
ui.startB.clicked.connect(startMeasuring)
ui.stopB.clicked.connect(stopMeasuring)
ui.saveFile.clicked.connect(led)
ui.clearB.clicked.connect(graphClear)
ui.newW.clicked.connect(newWinPlot)

# ui.pin3.stateChanged.connect(pin3Control)

ui.progLabel.setText(str(int(ui.dur.value()) * int(ui.speedRate.currentText())))
ui.progressBar.setValue(0)

ui.show()
sys.exit(app.exec())
