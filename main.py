# starting sudo from venv for port access:
# sudo -E env PATH=$PATH python main.py
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice
import json

app = QtWidgets.QApplication([])
ui = uic.loadUi("design.ui")
ui.setWindowTitle("Tremorograph ADXL345 v1.0")

serial = QSerialPort()
serial.setBaudRate(115200)
serial.setReadBufferSize(0)
portList = []
speedList = ["25", "50", "100", "200", "400"]
gravityList = ["2", "4", "8", "16"]
ports = QSerialPortInfo.availablePorts()
for port in ports:
    portList.append(port.portName())
ui.comL.addItems(portList)
ui.speedRate.addItems(speedList)
ui.gravityRange.addItems(gravityList)


# drate =""


def onRead():
    try:
        j = json.loads(str(serial.readAll(), 'utf-8'))
        print(type(j['led']))
        ui.term.appendPlainText(str(j['led']))
        # print(rx)
    except:
        rx = serial.readAll()
        rxs = str(rx, 'utf-8')
        ui.term.appendPlainText(rxs)
        print(rx)


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
    # print(drate)
    serialSend(s)


def startMeasuring():
    global duration
    duration = ui.dur.value()  # string for start: {"start":10} \\\10 sec
    s = {
        "start": str(duration)
    }
    # d = int(duration)
    # print(d*drate)
    serialSend(s)


def stopMeasuring():  # string for stop: {"stop":1}
    s = {
        "stop": 1
    }
    print("stop")
    serialSend(s)


def led():
    s = {
        "led": 1
    }
    serialSend(s)


# def pin3Control(val):
#     if val == 2: val = 1;
#     serialSend([2, val])


def setProgVal():
    ui.progLabel.setText(str(int(ui.dur.value()) * int(ui.speedRate.currentText())))


def setProgBar():
    i = int(str(int(ui.dur.value()) * int(ui.speedRate.currentText())))
    ui.progressBar.setValue(i)



ui.speedRate.currentIndexChanged.connect(setProgVal)
ui.dur.valueChanged.connect(setProgVal)


# def checkpPogress():
#     if ui.speedRate.currentTextChanged.connect() or ui.dur.valueChanged.connect():
#         print("12")


serial.readyRead.connect(onRead)
ui.openB.clicked.connect(onOpen)
ui.closeB.clicked.connect(onClose)
# ------------------------------------
ui.setB.clicked.connect(sendSettings)
ui.startB.clicked.connect(startMeasuring)
ui.stopB.clicked.connect(stopMeasuring)
ui.saveFile.clicked.connect(led)

# ui.pin3.stateChanged.connect(pin3Control)

ui.progLabel.setText(str(int(ui.dur.value()) * int(ui.speedRate.currentText())))
setProgBar()

ui.show()
sys.exit(app.exec())
