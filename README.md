# The tremor project
Tremorograph based on Arduino board + ADXL345 accelerometer module.
This device is measures hand shake. For doing measuring put sensor on hand and start measuring.
Modified ADXL345 SparkFun library for special options is included to "device" folder.
The device is using JSON over Serial protocol to communicate with desktop app.
Desktop app was made in Python and PyQt5.

$ pip install -r requirements.txt

The program is need to starting sudo from venv for port access:

(venv)~$ sudo -E env PATH=$PATH python main.py

# Some screenshots:

![Alt text](https://github.com/idramm25/tremor/blob/main/Images/qtdesigner.jpg?raw=true "Optional title")

![Alt text](https://github.com/idramm25/tremor/blob/main/Images/mainWindow.jpg?raw=true "Optional title")

![Alt text](https://github.com/idramm25/tremor/blob/main/Images/mainWindow1.jpg?raw=true "Optional title")

# Device:
![Alt text](https://github.com/idramm25/tremor/blob/main/Images/device.jpg?raw=true "Optional title")
