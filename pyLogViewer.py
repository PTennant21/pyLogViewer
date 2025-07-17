import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt # type: ignore
from PyQt5.QtWidgets import QAction, QApplication, QMainWindow, QPushButton, QLabel, QListWidget, QTableWidget, QTableWidgetItem, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QMenu # type: ignore

class InputWindow(QMainWindow): # input line that displays input in a label
    def __init__(self):
        super().__init__() # this initializes it with the mainwindows stuff i think

        self.filepath = "data.txt"
        self.setWindowTitle("pyLogViewer v0.3.1 - " + self.filepath ) # window name
        self.sortDown = True
        self.lastIndex = 0
        self.label = QLabel("Initializing...") # shows text.

        self.tableBox = QTableWidget()
        self.tableBox.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setDataTable(self.fileRead(self.filepath, True))

        self.inputBox = QLineEdit() # edit line. lets you edit text the line.
        self.inputBox.installEventFilter(self) # checks for enters

        self.buttonFprev = QPushButton("Find Next")
        self.buttonFnext = QPushButton("Find Prev")

        self.buttonBuddy = QPushButton("Open File") # button. it buttons.
        self.buttonBuddy.clicked.connect(self.reinit) # does whenever button clicked

        self.setMinimumSize(QSize(500, 300))
        self.resize(900, 500)

        self.toplabel_set("Click a header to sort.", self.tableBox)

        self.bottombar = QHBoxLayout() 
        self.bottombar.insertWidget(1, self.inputBox)
        self.bottombar.insertWidget(2, self.buttonFprev)
        self.bottombar.insertWidget(3, self.buttonFnext)
        self.bottombar.insertWidget(4, self.buttonBuddy)

        self.layout = QVBoxLayout() # object containing the layout, not window
        self.layout.addWidget(self.label) # text from the edited line
        self.layout.addWidget(self.tableBox) # table showing data
        self.layout.addLayout(self.bottombar) # the edit line
        #layout.addWidget(self.buttonBuddy) # button

        container = QWidget() # widget containing multiple laid out widgets
        container.setLayout(self.layout) # give it the layout!~

        self.setCentralWidget(container) # makes container central widget... so you can see


    # REINITIALIZATION!!! Brings everything to zero and reads a new file.
    def reinit(self):
        self.sortDown = True
        self.lastIndex = 0

        #self.data = self.fileRead(self.filepath, False)

        #self.toplabel_set("Clearing table...")
        #self.tableBox.clear()
        #self.tableBox.close()
        self.setDataTable(self.fileRead(self.filepath, False))

        # nothing else needed cuz the connections are still there
        #self.tableBox.resizeColumnsToContents()

        self.toplabel_set("Click a header to sort.", self.tableBox) # label yah
        self.setWindowTitle("pyLogViewer v0.3.1 - " + self.filepath ) # window     name
        self.layout.update()

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
        self.toplabel_set("Sorting " + ("descending" if self.sortDown else "ascending") + " by " + headerTxt, self.tableBox)

        self.tableBox.sortItems(logicalIndex, self.sortDown)

    def toplabel_set(self, action, table):
        if(table == -1):
            self.label.setText("Rows: N/A\n" + action)
        else:
            self.label.setText("Rows: " + str(table.rowCount()) + "\n" + action)

        app.processEvents()

    def fixup_date(self, date, type):
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        for i in range(len(month)):
            date = date.replace(month[i], str(i + 1).zfill(2))
        if(type == 1):
            return(date[2:])
        if(type == 2):
            date = date.split(" ")
            date[0] = date[0].split("-")
            return(date[0][2] + "-" + date[0][1] + "-" + date[0][0] + " " + date[1])

    def fileRead(self, path, init):
        self.toplabel_set("Parsing file " + self.filepath + "...", -1)

        if(init):
            with(open(path, 'r')) as logfile:
                data = logfile.read().replace("\n\n", "\n").split("\n") # removes all of the blanks between lines.
        else:
            try: # checks if file even exists otherwise it exits and nothing ever happens
                with(open(self.inputBox.text(), 'r')) as logfile:
                    data = logfile.read().replace("\n\n", "\n").split("\n") # removes excess newlines
            
                self.filepath = self.inputBox.text()
            except:
                print("FILE NOT FOUND.")
                self.inputBox.clear()
                self.toplabel_set("Filepath not found.", -1)
                #self.layout.update()
                return -1

        self.toplabel_set("Formatting data from " + self.filepath + "...", -1)

        v = 0
        while v < len(data): # removes blanklines. separated in order to have correct amnt of leading order 0s
            if(data[v].isspace() or (len(data[v]) <= 1)):
                data.pop(v)
                v -= 1
            else:
                data[v] = data[v].split(" ") 
                print(data[v])
            v += 1

        return data
    
    def setDataTable(self, data):

        #table = QTableWidget()
        #table.setEditTriggers(QTableWidget.NoEditTriggers)
        if(data == -1):
            return
        
        self.tableBox.clear()
        self.tableBox.setRowCount(len(data))
        self.tableBox.setColumnCount(11)
        self.tableBox.setHorizontalHeaderLabels(["IP Address", "Day", "Date1", "Date2", "Computer", "User", "Process", "New", "Old", "Min", "Max"])
    
        self.toplabel_set("Adding data from " + self.filepath + "...", -1)

        for y in range(len(data)):
            offset = 0
            print("\nL" + str(y+1), end = ': ')
            for x in range(15):
                print(x, end = ':')
                if(x in range(len(data[y]))):
                    if(x == 2):
                        item = QTableWidgetItem(self.fixup_date(data[y][5] + "-" + data[y][2] + "-" + data[y][3] + " " + data[y][4], 1))
                        print("A", end = '.')
                        x = 5
                        offset = -3
                    elif(x == 6):
                        item = QTableWidgetItem(self.fixup_date(data[y][6] + " " + data[y][7], 2))
                        print("B", end = '.')
                        x = 7
                        offset = -4
                    elif(x < 2 or x > 7):
                        item = QTableWidgetItem(data[y][x]) # sets each widget item in the tables slots.
                    else:
                        item = -1
                else:
                    item = QTableWidgetItem("N/A") # default message if current row has less columns
                    print("e", end = '.')

                if(item != -1):
                    self.tableBox.setItem(y, x + offset, item)
                    print("add", end = ' ')
                else:
                    print("_", end = '')
        print("")

        self.tableBox.resizeColumnsToContents()
        self.tableBox.horizontalHeader().sectionClicked.connect(self.tablefunc_sort)

app = QApplication(sys.argv)
window = InputWindow()
window.show()
app.exec()