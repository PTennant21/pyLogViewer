import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt # type: ignore
from PyQt5.QtWidgets import QAction, QApplication, QMainWindow, QPushButton, QLabel, QListWidget, QTableWidget, QTableWidgetItem, QLineEdit, QVBoxLayout, QWidget, QMenu # type: ignore

class InputWindow(QMainWindow): # input line that displays input in a label
    def __init__(self):
        super().__init__() # this initializes it with the mainwindows stuff i think

        self.filepath = "data.txt"
        self.setWindowTitle("pyLogViewer v0.3.0 - " + self.filepath ) # window name
        self.actionTxt = "Click a header to sort."
        self.sortDown = True
        self.lastIndex = 0

        with(open(self.filepath, 'r')) as logfile:
            self.data = logfile.read().replace("\n\n", "\n").split("\n") # removes all of the blanks between lines.

        v = 0
        while v < len(self.data): # removes blank lines. separated in order to have correct amnt of leading 0s
            if(self.data[v].isspace() or (len(self.data[v]) <= 1)):
                self.data.pop(v)
                v -= 1
            v += 1

        v = 0
        while v < len(self.data): # splits str lines into list
            self.data[v] = [str(v + 1).zfill(len(str(len(self.data))))] + self.data[v].split(" ") 
            print(self.data[v])
            v += 1
        
        self.tableBox = QTableWidget()
        self.tableBox.setRowCount(len(self.data))
        self.tableBox.setColumnCount(16)
        self.tableBox.setHorizontalHeaderLabels(["Line", "IP Address", "Day", "Month", "Date", "Time", "Year", "Date2", "Time2", "Computer", "User", "Process", "New", "Old", "Min", "Max"])

        for x in range(len(self.data)):
            for y in range(16):
                if(y in range(len(self.data[x]))):
                    item = QTableWidgetItem(self.data[x][y]) # sets each widget item in the tables slots.
                else:
                    item = QTableWidgetItem("N/A") # default message if current row has less columns
                self.tableBox.setItem(x, y, item)

        self.tableBox.resizeColumnsToContents()
        self.tableBox.horizontalHeader().sectionClicked.connect(self.tablefunc_sort)

        self.inputBox = QLineEdit() # edit line. lets you edit text the line.
        self.inputBox.installEventFilter(self) # checks for enters

        self.buttonBuddy = QPushButton("Open File") # button. it buttons.
        self.buttonBuddy.clicked.connect(self.reinit) # does whenever button clicked

        self.label = QLabel("Rows: " + str(self.tableBox.rowCount()) + "\n" + self.actionTxt) # i think this is just the thing that shows text..?

        self.setMinimumSize(QSize(250, 200))
        self.resize(900, 500)

        layout = QVBoxLayout() # object containing the layout, not window
        layout.addWidget(self.label) # text from the edited line
        layout.addWidget(self.tableBox) # table showing data
        layout.addWidget(self.inputBox) # the edit line
        layout.addWidget(self.buttonBuddy) # button

        container = QWidget() # widget containing multiple laid out widgets
        container.setLayout(layout) # give it the layout!~

        self.setCentralWidget(container) # makes container central widget... so you can see


    # REINITIALIZATION!!! Brings everything to zero and reads a new file.
    def reinit(self):
        self.actionTxt = "Click a header to sort."
        self.sortDown = True
        self.lastIndex = 0

        try: # checks if file even exists otherwise it exits and nothing ever happens
            with(open(self.inputBox.text(), 'r')) as logfile:
                self.data = logfile.read().replace("\n\n", "\n").split("\n") # removes excess newlines
            
            self.filepath = self.inputBox.text()
        except:
            print("FILE NOT FOUND.")
            self.actionTxt = "Filepath not found."
            self.inputBox.clear()
            self.toplabel_set()
            return

        v = 0
        while v < len(self.data): # removes blanklines. separated in order to have correct amnt of leading order 0s
            if(self.data[v].isspace() or (len(self.data[v]) <= 1)):
                self.data.pop(v)
                v -= 1
            v += 1

        v = 0
        while v < len(self.data): # splits str lines into list
            self.data[v] = [str(v + 1).zfill(len(str(len(self.data))))] + self.data[v].split(" ") 
            print(self.data[v])
            v += 1

        self.tableBox.clear()
        self.tableBox.setRowCount(len(self.data))
        self.tableBox.setColumnCount(16)
        self.tableBox.setHorizontalHeaderLabels(["Order", "IP Address", "Day", "Month", "Date", "Time", "Year", "Date2", "Time2", "Computer", "User", "Process", "New", "Old", "Min", "Max"])

        for x in range(len(self.data)):
            for y in range(16):
                if(y in range(len(self.data[x]))):
                    item = QTableWidgetItem(self.data[x][y]) # sets each widget item in the tables slots.
                else:
                    item = QTableWidgetItem("N/A") # default message if current row has less columns
                self.tableBox.setItem(x, y, item)

        # nothing else needed cuz the connections are still there
        self.tableBox.resizeColumnsToContents()
        self.inputBox.clear()
        self.toplabel_set # label yah
        self.setWindowTitle("pyLogViewer v0.3.0 - " + self.filepath ) # window     name




    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.inputBox:
            if event.key() == QtCore.Qt.Key_Return and self.inputBox.hasFocus():
                print('Enter pressed')
                #LIST self.listBox.addItem(self.inputBox.text())
                #self.inputBox.clear()
                self.reinit()
                #LIST self.label.setText(self.filepath + "\nItems: " + str(self.listBox.count()))

        return super().eventFilter(obj, event)

    def tablefunc_sort(self, logicalIndex): # sorts the selected column when a column header is selected
        headerTxt = self.tableBox.horizontalHeaderItem(logicalIndex).text()
        if(logicalIndex != self.lastIndex):
            self.sortDown = True
            self.lastIndex = logicalIndex
        else:
            self.sortDown = not self.sortDown

        print(logicalIndex)
        self.actionTxt = "Sorting " + ("descending" if self.sortDown else "ascending") + " by " + headerTxt
        self.toplabel_set()

        self.tableBox.sortItems(logicalIndex, self.sortDown)

    def toplabel_set(self):
        self.label.setText("Rows: " + str(self.tableBox.rowCount()) + "\n" + self.actionTxt)

app = QApplication(sys.argv)
window = InputWindow()
window.show()
app.exec()