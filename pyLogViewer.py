import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt # type: ignore
from PyQt5.QtWidgets import QAction, QApplication, QMessageBox, QDialog, QFileDialog, QMainWindow, QPushButton, QLabel, QListWidget, QTableWidget, QTableWidgetItem, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QMenu # type: ignore

class LogWindow(QMainWindow): # The entire window.
    def __init__(self):
        super().__init__() # this initializes it with the mainwindow

        self.filepath = "data.txt"
        self.setWindowTitle("pyLogViewer v0.4.0 - " + self.filepath) # window name
        self.sortDown = True
        self.lastIndex = 0
        self.label = QLabel("Initializing...") # shows text.
        self.errortext = False
        self.searchlist = -1
        self.lastsearch = -1
        self.lastrow = 0
        self.lastcolumn = 0

        self.tableBox = QTableWidget()
        self.tableBox.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setDataTable(self.fileRead(self.filepath, True)) # most important line. sorts the data and passes it to setdatatable and sorts it further and puts it in the table.
        #self.tableBox.horizontalHeader().sectionClicked.connect(lambda:self.toplabel_set("Sorting...", self.tableBox))
        self.tableBox.horizontalHeader().sectionClicked.connect(self.tablesort)
        #self.tableBox.horizontalHeader().sectionPressed.connect(lambda:self.toplabel_set("winning...", self.tableBox))

        self.inputBox = QLineEdit() # edit line. lets you edit text in the line.
        self.inputBox.installEventFilter(self) # checks for enters

        self.buttonFprev = QPushButton("Find Next")
        self.buttonFprev.clicked.connect(lambda : self.jumptosearch(1)) # lambda makes small anonymous functions. can't connect a method with an argument so this is needed
        self.buttonFnext = QPushButton("Find Prev")
        self.buttonFnext.clicked.connect(lambda : self.jumptosearch(-1))

        self.buttonBuddy = QPushButton("Open File") # button.
        self.buttonBuddy.clicked.connect(self.filePrompt) # does whenever button clicked

        self.setMinimumSize(QSize(500, 300))
        self.resize(900, 500)

        self.toplabel_set("Click a header to sort.", self.tableBox)

        self.bottombar = QHBoxLayout() 
        self.bottombar.insertWidget(1, self.inputBox)
        self.bottombar.insertWidget(2, self.buttonFprev)
        self.bottombar.insertWidget(3, self.buttonFnext)
        self.bottombar.insertWidget(4, self.buttonBuddy) # button

        self.layout = QVBoxLayout() # object containing the layout, not window
        self.layout.addWidget(self.label) # text from the edited line
        self.layout.addWidget(self.tableBox) # table showing data
        self.layout.addLayout(self.bottombar) # the edit line

        container = QWidget() # widget containing multiple laid out widgets
        container.setLayout(self.layout) # give it layout!~

        self.setCentralWidget(container) # makes container central widget... so you can see

    def tablesearch(self, value):
        if(value == self.lastsearch):
            return
        else:
            self.lastsearch = value

        self.searchlist = self.tableBox.findItems(value, Qt.MatchFlag.MatchContains)
        self.searchindex = 0

    def tempjump(self):
        self.tableBox.setCurrentCell(self.tableBox.rowCount() - 3, self.tableBox.columnCount() - 3)

    def jumptosearch(self, dir):
        self.toplabel_set("Searching...", self.tableBox)
        QApplication.setOverrideCursor(Qt.WaitCursor)

        search = self.inputBox.text() # variable so i dont have to type all that
        if(search != self.lastsearch): # resets starting pos for new searches
            self.lastrow = 0 if dir > 0 else self.tableBox.rowCount() - 1
            self.lastcolumn = 0 if dir > 0 else self.tableBox.columnCount() - 1
            self.searchlist = []

        if(search == "" or search.isspace()): # returns if its nothing.
            self.toplabel_set("No search value entered.", self.tableBox)
            QApplication.restoreOverrideCursor()
            return
        
        searched = 1 # set it to 1 to account for the index starting at zero
        row = self.lastrow
        column = self.lastcolumn
        
        while row in range(self.tableBox.rowCount()): # goes through every row.
            while column in range(self.tableBox.columnCount()): # goes through every column.
                #print("Searching " + str(row) + ", " + str(column))

                # if the string was found, AND EITHER this is a new search OR this isnt the last found location
                if(self.tableBox.item(row, column).text().find(search) != -1 and (self.lastsearch != search or (self.lastrow != row or self.lastcolumn != column))):
                    self.tableBox.setCurrentCell(row, column) # highlight and go to is
                    
                    #print("found at " + str(row) + ", " + str(column))
                    self.searchlist.append([row, column])
                    self.lastsearch = search # this is the last search
                    self.lastrow = row # last row found at
                    self.lastcolumn = column # last column found at
                    self.toplabel_set("Found " + str(len(self.searchlist)) + " items...", self.tableBox)
                    #QApplication.restoreOverrideCursor()
                    #return
                
                searched += 1 # when this is larger than the amt of table items, return as there are no matches.
                if(searched > self.tableBox.rowCount() * self.tableBox.columnCount()):
                    print("no results found.")
                    self.toplabel_set("Value not found.", self.tableBox)
                    QApplication.restoreOverrideCursor()
                    return
                
                column += dir # move column in specified direction.

            column = 0 if dir > 0 else self.tableBox.columnCount() - 1 # reset column based on direction
            row += dir # move row in specified direction.

            if(row >= self.tableBox.rowCount()): # makes row 0 if it is above range
                row = 0
            if(row < 0): # makes row highest if it is below range
                row = self.tableBox.rowCount() - 1


# it works ig..?
                

    def filePrompt(self):
        prompt = QFileDialog(self)
        prompt.setWindowTitle("Select a file.")
        prompt.setMinimumSize(QSize(500, 300))
        prompt.resize(600, 400)
        prompt.setFileMode(QFileDialog.FileMode.ExistingFile)
        prompt.setViewMode(QFileDialog.ViewMode.Detail)
        #prompt.exec()
        #print(prompt.getOpenFileName()[0])
        filepath = self.filepath
        self.filepath = prompt.getOpenFileName()[0]
        #print(self.filepath)
        if(self.filepath != ""):
            self.setWindowTitle("pyLogViewer v0.4.0 - " + self.filepath)
            self.reinit()

    def tempPrompt(self):
        prompt = QMessageBox(self)
        prompt.setWindowTitle("Warning")
        #prompt.setMinimumSize(QSize(500, 300))
        #prompt.resize(600, 400)
        prompt.setText("This button doesn't do anything yet.")

        prompt.exec()
        print("Ok.")

    def eventFilter(self, obj, event): # checks if key enter has been pressed when inputbox is in focus
        if event.type() == QtCore.QEvent.KeyPress and obj is self.inputBox:
            if event.key() == QtCore.Qt.Key_Return and self.inputBox.hasFocus():
                print('Enter pressed')
                self.filepath = self.inputBox.text()
                self.reinit()
        return super().eventFilter(obj, event)

    def reinit(self): # REINITIALIZATION!!! Brings everything to zero and reads a new file.
        self.sortDown = True # always sort descending by default
        self.lastIndex = 0 # last selected column, 0 is default
        try:
            self.setDataTable(self.fileRead(self.filepath, False)) # adds cleaned up data array to the data table
            self.lastsearch = -1 # reset search vars for new files
            self.lastrow = 0
            self.lastcolumn = 0 
        except:
            self.tableBox.clear()
            self.filepath = -1
            self.toplabel_set("Error with selected file.", -1)
            self.errortext = True
            return

        self.toplabel_set("Click a header to sort.", self.tableBox) # its a label alright
        self.setWindowTitle("pyLogViewer v0.4.0 - " + self.filepath ) # window name

    def tablesort(self, logicalIndex): # sorts the selected column when... a column header is selected.
        self.toplabel_set("Sorting...", self.tableBox)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        #self.errortext = True
        headerTxt = self.tableBox.horizontalHeaderItem(logicalIndex).text()
        if(logicalIndex != self.lastIndex):
            self.sortDown = True
            self.lastIndex = logicalIndex
        else:
            self.sortDown = not self.sortDown

        print("column" + str(logicalIndex))
        
        self.tableBox.sortItems(logicalIndex, self.sortDown)
        self.toplabel_set("Sorting " + headerTxt + (" descending" if self.sortDown else " ascending"), self.tableBox)
        QApplication.restoreOverrideCursor()

    def toplabel_set(self, action, table): # sets the top label to all sorts of things.
        if(self.errortext): # stops error text from insta disappearing. probably a better way to do this
            self.errortext = False
            print("err false return : " + action)
            return
        #print("I haven't returned!")
        if(table == -1):
            self.label.setText("Rows: N/A\n" + action)
        else:
            self.label.setText("Rows: " + str(table.rowCount()) + "\n" + action)
        #print("setting the text now : " + action)
        app.processEvents() # this just makes it actively update so the user knows it ain't dead

    def fixup_date(self, date, type): # this formats the dates in both date1 and date2 to be uniform and sortable!
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        for i in range(len(month)):
            date = date.replace(month[i], str(i + 1).zfill(2))
        if(type == 1):
            return(date[2:])
        if(type == 2):
            date = date.split(" ")
            date[0] = date[0].split("-")
            return(date[0][2] + "-" + date[0][1] + "-" + date[0][0] + " " + date[1])

    def fileRead(self, path, init): # this goes through the txt file, removes all blank lines and returns it as a 2D list.
        self.toplabel_set("Parsing file " + self.filepath + "...", -1)
        QApplication.setOverrideCursor(Qt.WaitCursor)

        if(init):
            with(open(path, 'r')) as logfile:
                data = logfile.read().replace("\n\n", "\n").split("\n") # removes all of the blanks between lines.
        else:
            try: # checks if file even exists otherwise it exits and nothing ever happens
                with(open(self.filepath, 'r')) as logfile:
                    data = logfile.read().replace("\n\n", "\n").split("\n") # removes excess newlines

                #self.filepath = self.inputBox.text()
            except:
                print("FILE NOT FOUND.")
                self.inputBox.clear()
                self.toplabel_set("Filepath not found.", -1)
                self.errortext = True
                #self.layout.update()
                QApplication.restoreOverrideCursor()
                return -1

        self.toplabel_set("Formatting data from " + self.filepath + "...", -1)

        v = 0
        while v < len(data): # removes blanklines and splits full lines into space-based lists
            if(data[v].isspace() or (len(data[v]) <= 1)):
                data.pop(v)
                v -= 1
            else:
                data[v] = data[v].split(" ") 
                #print(data[v])
            v += 1

        QApplication.restoreOverrideCursor()
        return data
    
    def setDataTable(self, data): # sets the tablewidget with data from a 2d list
        if(data == -1):
            return
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.tableBox.clear()
        self.tableBox.setRowCount(len(data))
        self.tableBox.setColumnCount(11)
        self.tableBox.setHorizontalHeaderLabels(["IP Address", "Day", "Date1", "Date2", "Computer", "User", "Process", "New", "Old", "Min", "Max"])
    
        self.toplabel_set("Adding data from " + self.filepath + "...", -1)

        for y in range(len(data)):
            offset = 0
            #print("\nL" + str(y+1), end = ': ')
            for x in range(15):
                #print(x, end = ':')
                if(x in range(len(data[y]))):
                    if(x == 2):
                        item = QTableWidgetItem(self.fixup_date(data[y][5] + "-" + data[y][2] + "-" + data[y][3] + " " + data[y][4], 1))
                        #print("A", end = '.')
                        x = 5
                        offset = -3
                    elif(x == 6):
                        item = QTableWidgetItem(self.fixup_date(data[y][6] + " " + data[y][7], 2))
                        #print("B", end = '.')
                        x = 7
                        offset = -4
                    elif(x < 2 or x > 7):
                        item = QTableWidgetItem(data[y][x]) # sets each widget item in the tables slots.
                    else:
                        item = -1
                else:
                    item = QTableWidgetItem("N/A") # default message if current row has less columns
                    #print("e", end = '.')

                if(item != -1):
                    self.tableBox.setItem(y, x + offset, item)
                    #print("add", end = ' ')
                #else:
                    #print("_", end = '')
                
        #print("")
    
        self.tableBox.resizeColumnsToContents()
        QApplication.restoreOverrideCursor()
# end of classk

app = QApplication(sys.argv)
window = LogWindow()
window.show()
app.exec()