import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt # type: ignore
from PyQt5.QtWidgets import QAction, QApplication, QMainWindow, QPushButton, QLabel, QListWidget, QTableWidget, QTableWidgetItem, QLineEdit, QVBoxLayout, QWidget, QMenu # type: ignore


class InputWindow(QMainWindow): # input line that displays input in a label
    def __init__(self):
        super().__init__() # this initializes it with the mainwindows stuff i think

        self.setWindowTitle("pyLogViewer v0.2.0") # window name
        self.filepath = "data.txt"

        with(open(self.filepath, 'r')) as logfile:
            self.data = logfile.read().replace("\n\n", "\n").split("\n") # removes all of the blanks between lines.

        v = 0
        while v < len(self.data): # removes blank values and optionally splits str into list
            if(self.data[v].isspace() or (len(self.data[v]) <= 1)):
                self.data.pop(v)
                v -= 1
            else:
                self.data[v] = self.data[v].split(" ") 
                print(self.data[v])
            v += 1
        
        self.tableBox = QTableWidget()
        self.tableBox.setRowCount(len(self.data))
        self.tableBox.setColumnCount(15)
        self.tableBox.setHorizontalHeaderLabels(["IP Address", "Day", "Month", "Date", "Time", "Year", "Date2", "Time2", "Computer", "User", "Process", "New", "Old", "Min", "Max"])

        for x in range(len(self.data)):
            for y in range(15):
                if(y in range(len(self.data[x]))):
                    item = QTableWidgetItem(self.data[x][y]) # sets each widget item in the tables slots.
                else:
                    item = QTableWidgetItem("N/A") # default message if current row has less columns
                self.tableBox.setItem(x, y, item)

        self.tableBox.resizeColumnsToContents()

        #LIST self.listBox = QListWidget()
        #LIST self.listBox.addItems(self.data)

        self.inputBox = QLineEdit() # this is... an edit line. it lets you edit text on the line.
        self.inputBox.installEventFilter(self)

        #LIST self.label = QLabel(self.filepath + "\nItems: " + str(self.listBox.count())) # i think this is just the thing that shows text..?
        self.label = QLabel("\nRows: " + str(self.tableBox.rowCount()) + "\nColumns: " + str(self.tableBox.columnCount())) # i think this is just the thing that shows text..?


        layout = QVBoxLayout() # this is an object containing the layout, not the actual window
        layout.addWidget(self.label) # the text from the edited lone
        layout.addWidget(self.tableBox)
        layout.addWidget(self.inputBox) # the edit line

        container = QWidget() # seems be a widget containing multiple laid out widgets...?
        container.setLayout(layout) # give it the layout!~

        self.setCentralWidget(container) # makes the container the central widget... so you can see anything

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.inputBox:
            if event.key() == QtCore.Qt.Key_Return and self.inputBox.hasFocus():
                print('Enter pressed')
                #LIST self.listBox.addItem(self.inputBox.text())
                self.inputBox.clear()
                #LIST self.label.setText(self.filepath + "\nItems: " + str(self.listBox.count()))

        return super().eventFilter(obj, event)

app = QApplication(sys.argv)
window = InputWindow()
window.show()
app.exec()