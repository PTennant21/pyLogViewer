import sys, time # imports system and time modules
from PyQt5 import QtCore # imports qtcore module
from PyQt5.QtCore import QSize, Qt # imports qsize and qt classes
from PyQt5.QtWidgets import (QApplication, QSpinBox, QCheckBox, QFileDialog, QMainWindow, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QStackedLayout, QWidget) # imports.. a lot of widget classes

class LogWindow(QMainWindow): # The window class
    def __init__(self): # initializes class values
        super().__init__() # initializes it with mainwindow
        self.filepath = "data.txt"
        self.version = "v0.6.1"
        self.setWindowTitle("pyLogViewer " + self.version + " - " + self.filepath)
        self.sortDown = True # always sort columns descending by default
        self.lastIndex = 0 # last selected column, 0 is default
        self.searchlist = -1 # contains items which match current search
        self.lastsearch = -1 # the last search, as a string. used for comparison to current search
        self.searchindex = -1 # which position in the searchlist the user is at

        self.label = QLabel("Initializing...")
        
        self.refreshLabel = QLabel("Refresh:")
        self.refreshLabel.setToolTip("The amount of seconds until the list is automatically refreshed.")
        self.refreshBox = QSpinBox() # editable line, contains search value

        self.maxLabel = QLabel("Max:")
        self.maxlineBox = QSpinBox() # editable line, contains search value
        self.maxlineBox.setMaximum(1000000)
        self.maxlineBox.setSingleStep(10000)
        self.maxlineBox.setValue(150000) # maximum amount of lines to read
        self.maxlineBox.setGroupSeparatorShown(True)

        self.tableBox = QTableWidget() # table, contains and shows data
        self.tableBox.setEditTriggers(QTableWidget.NoEditTriggers) # prevents editing of table items
        self.fileRead() # sorts the data and passes it to tablebox
        self.tableBox.horizontalHeader().sectionClicked.connect(lambda logicalindex: self.tablesort(logicalindex, self.tableBox)) # allows for sorting via header click
        #useless self.table = self.tableBox

        self.lineBox = QTableWidget() # contains every line with a matching search item. takes longer, but faster than highlighting.
        self.lineBox.setEditTriggers(QTableWidget.NoEditTriggers) # prevents editing of table items
        self.lineBox.horizontalHeader().sectionClicked.connect(lambda logicalindex: self.tablesort(logicalindex, self.lineBox)) # allows for sorting via header click

        self.inputBox = QLineEdit() # editable line, contains search value
        self.inputBox.installEventFilter(self) # checks for enter presses
        self.inputBox.setPlaceholderText("Enter a value to search.")

        self.caseCheck = QCheckBox("Case sensitive?")
        self.caseCheck.stateChanged.connect(lambda : self.clearsearch(False)) # clears search so the next one re-evaluates the list with new conditions

        self.buttonSprev = QPushButton("Find Prev") # prev result of search
        self.buttonSprev.clicked.connect(lambda : self.searchtable(-1)) # can't connect a method with an argument so lambda is needed
        self.buttonSprev.setToolTip("Find a previous instance of the value in the search box.")

        self.buttonSnext = QPushButton("Find Next") # next result of search
        self.buttonSnext.clicked.connect(lambda : self.searchtable(1))
        self.buttonSnext.setToolTip("Find a next instance of the value in the search box.")

        self.buttonFile = QPushButton("Open File")
        self.buttonFile.clicked.connect(self.filePrompt) # opens a file prompt when the button is clicked
        self.buttonFile.setToolTip("Import data from a new file.")

        self.setMinimumSize(QSize(510, 200))
        self.resize(900, 500)

        self.topbar = QHBoxLayout()
        self.topbar.insertWidget(1, self.label)
        self.topbar.addStretch(2)
        self.topbar.insertWidget(3, self.maxLabel)
        self.topbar.insertWidget(4, self.maxlineBox)
        self.topbar.insertWidget(5, self.refreshLabel)
        self.topbar.insertWidget(6, self.refreshBox)

        self.tables = QStackedLayout()
        self.tables.addWidget(self.tableBox)
        self.tables.addWidget(self.lineBox)

        self.bottombar = QHBoxLayout() # horizontal layout, allows multiple widgets going horizontally. used for the search box and buttons
        self.bottombar.insertWidget(1, self.buttonFile)
        self.bottombar.insertWidget(2, self.inputBox)
        self.bottombar.insertWidget(3, self.buttonSprev)
        self.bottombar.insertWidget(4, self.buttonSnext)
        self.bottombar.insertWidget(5, self.caseCheck)

        self.toplabel_set("Click a header to sort, or use the box to search.", self.tableBox)

        self.layout = QVBoxLayout() # object containing the vertical layout
        self.layout.addLayout(self.topbar)
        self.layout.addLayout(self.tables)
        self.layout.addLayout(self.bottombar) # the entire horizontal search layout. they can be nested... how useful!

        self.container = QWidget() # widget containing multiple laid out widgets
        self.container.setLayout(self.layout) # give it the layout!~

        self.setCentralWidget(self.container) # makes the container the central widget

    def clearsearch(self, fullclear): # clears the search variables. prevents issues and forces next search to occur
        self.searchlist = -1
        self.searchindex = -1
        self.lastsearch = -1

        if(fullclear):
            self.tables.setCurrentIndex(0)
            self.lineBox.clear()

    def searchtable(self, dir): # creates list of all occurrences of specified value and subsequently proceeds through it
        search = self.inputBox.text() # the current input from the input box widget

        if(search == None or search == ""): # TODO: this block returns the view to the standard table and deletes all the search stuff.
            self.toplabel_set("No search value entered.", self.tableBox) # does this if you try to search nothing for some reason
            self.lineBox.clearSelection() # removes selections in table widget
            self.tables.setCurrentIndex(0)
            self.searchindex = -2
            return # exit the method.

        # executed on repeat searches. it moves you to the next value in the selected direction.
        if(self.lastsearch == search): # executed if its a repeat of the same search
            if(self.tables.currentIndex != 1):
                self.tables.setCurrentIndex(1)

            self.searchindex += (dir) # moves selection in direction. rhymes

            if(self.searchindex not in range(len(self.searchlist))):
                self.searchindex = 0 if dir != -1 else len(self.searchlist) - 1

            self.toplabel_set("Viewing " + f"{self.searchindex + 1:,}" + " of " + f"{len(self.searchlist):,}" + ' results for "' + search + '".', self.lineBox) # result you're viewing out of total
            self.lineBox.setCurrentCell(self.searchlist[self.searchindex][0], self.searchlist[self.searchindex][1]) # highlight and go to new selection
            return # exit the method.


        # executed on new searches, sets the result list and initial position.
        self.toplabel_set("Searching...", self.tableBox)
        QApplication.setOverrideCursor(Qt.WaitCursor)

        self.tableBox.clearSelection() # removes selections in table widget
        self.searchlist = [] # puts all items from table into list
        self.lineBox.clear()
        self.lineBox.setRowCount(self.tableBox.rowCount())
        self.lineBox.setColumnCount(self.tableBox.columnCount())
        self.lineBox.setHorizontalHeaderLabels(["IP Address", "Day", "New Date", "Old Date", "Computer", "User", "Process Variable", "New", "Old", "Min", "Max"])

        foundrow = False # checks if it's already saved this row.
        temprow = 0
        
        for row in range(self.tableBox.rowCount()):
            foundrow = False
            for col in range(self.tableBox.columnCount()):
                if((not self.caseCheck.isChecked() and self.tableBox.item(row, col).text().lower().find(search.lower()) != -1) or self.tableBox.item(row, col).text().find(search) != -1):
                    self.searchlist.append([temprow, col])
                    if(not foundrow):
                        for tempcol in range(self.tableBox.columnCount()): # sets next row in lineBox with all items in the found row
                            self.lineBox.setItem(temprow, tempcol, QTableWidgetItem(self.tableBox.item(row, tempcol).text()))
                        temprow += 1
                        foundrow = True

        if(len(self.searchlist) > 0): # goes to the first or last value if the searchlist has results.
            self.lineBox.setRowCount(temprow)
            self.lineBox.resizeColumnsToContents()
            self.tables.setCurrentIndex(1)
            self.searchindex = 0 if dir != -1 else len(self.searchlist) - 1
            self.lineBox.setCurrentCell(self.searchlist[0 if dir == 1 else dir][0], self.searchlist[0 if dir == 1 else dir][1]) # go to the first result
            self.toplabel_set("Viewing " + f"{self.searchindex + 1:,}" + " of " + f"{len(self.searchlist):,}" + ' results for "' + search + '".', self.lineBox)
            self.lastsearch = search 
        else:
            self.lineBox.clearSelection() # removes selections in table widget
            self.toplabel_set('No results for "' + search + '".', self.tableBox)
            self.tables.setCurrentIndex(0)
            self.lastsearch = -1
        
        app.processEvents()


        QApplication.restoreOverrideCursor()
                
    def filePrompt(self): # prompts user for a file using QFileDialog class
        prompt = QFileDialog(self) # init var with class
        prompt.setFileMode(QFileDialog.FileMode.ExistingFile) # open existing file
        prompt.setViewMode(QFileDialog.ViewMode.Detail) # shows greater detail in explorer
        self.filepath = prompt.getOpenFileName(self, "Select a file.", None, "Log Files (*.log);;Text Files (*.txt);;All Files (*)",)[0] # opens window itself and returns filepath. includes text and supported filetypes.
        if(self.filepath != ""): # make sure it is actually something
            self.setWindowTitle("pyLogViewer " + self.version + " - " + self.filepath) # visual filepath indicator
            self.reinit() # reload the file and reinitialize nearly everything

    def eventFilter(self, obj, event): # checks if key enter has been pressed when inputbox is in focus. these vars are in the class already
        if event.type() == QtCore.QEvent.KeyPress and obj is self.inputBox: # if there is a key press event...
            if event.key() == QtCore.Qt.Key_Return and self.inputBox.hasFocus(): # and the pressed key is return... and the input box is in focus...
                self.searchtable(1) # then SEARCH the table! pressing enter with the box goes forwards.
        return super().eventFilter(obj, event)

    def reinit(self): # REINITIALIZATION!!! Brings everything to zero and reads a new file.
        self.sortDown = True # always sort descending by default
        self.lastIndex = 0 # last selected column, 0 is default
        self.clearsearch(True) # clears the search variables
        try: # if the code fails, the exception is handled.
            self.fileRead() # reads file and adds data to the data table
        except:
            self.tableBox.clear() # empty the box
            self.filepath = -1 # set no filepath
            self.toplabel_set("Error with selected file.", -1) # this one is self explanatory i think.
            QApplication.restoreOverrideCursor() # restores the cursor cuz setdatatable is usually cut off before it does
            return # LEAVE!

        self.toplabel_set("Click a header to sort.", self.tableBox) # its a label alright
        self.setWindowTitle("pyLogViewer " + self.version + " - " + self.filepath) # window name

    def tablesort(self, logicalIndex, table): # sorts the selected column when... a column header is selected.
        self.toplabel_set("Sorting...", table) # loading message you know the drill by now
        QApplication.setOverrideCursor(Qt.WaitCursor) # loading cursor.
        headerTxt = table.horizontalHeaderItem(logicalIndex).text() # the header text to show later
        if(logicalIndex != self.lastIndex): # checks if this index is the same as the last one sorted
            self.sortDown = True # if not, it will always start sorted descending
            self.lastIndex = logicalIndex # sets the last index to this one
        else: # if so, it will sort the opposite of last time
            self.sortDown = not self.sortDown # yeah. inversion
        
        table.sortItems(logicalIndex, self.sortDown) # sorts the items at specified index
        self.toplabel_set("Sorting " + headerTxt + (" descending" if self.sortDown else " ascending"), table) # tells user how its sorted

        self.clearsearch(False) # clears the search variables, they will be incorrect otherwise
        QApplication.restoreOverrideCursor() # no more loading cursor.

    def toplabel_set(self, action, table): # sets the top label to all sorts of things.
        if(table == -1): # -1 replaces the table in some instances to avoid displaying row count
            self.label.setText("Rows: N/A\n" + action) # yeah.
        else: # otherwise
            self.label.setText("Rows: " + f"{self.tableBox.rowCount():,}" + "\n" + action) # it's just the row count !
        app.processEvents() # this just makes the application display actively update so the user knows it isn't dead

    def fixup_date(self, date, type): # formats the dates in either date1 or date2 to be uniform and sortable! ADD THIS TO MAIN LOOP.
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"] # those are all of the months, if you didn't know
        
        for i in range(len(month)): # goes through said all of the months
            date = date.replace(month[i], str(i + 1).zfill(2)) # replaces months with numbers when it finds them. this actually isn't too efficient.. RESEARCH other ways
        if(type == 1): # date1 is already formatted well
            return(date[2:]) # returns the string from third digit of year.
        if(type == 2): # date2 is messed up and must be rearranged.
            date = date.split(" ") # splits at space
            date[0] = date[0].split("-") # splits the data at dashes
            return(date[0][2] + "-" + date[0][1] + "-" + date[0][0] + " " + date[1]) # rearranges the date and time to be sortable and in line with date1

    def fileRead(self): # this goes through the txt file, removes all blank lines and returns it as a 2D list.

        self.toplabel_set("Parsing file...", -1)
        QApplication.setOverrideCursor(Qt.WaitCursor)

        try: # checks if file even exists otherwise it exits and nothing ever happens
            with(open(self.filepath, 'r')) as logfile:
                    data = logfile.read()
                    data = data.split("\n") # removes blanks between lines and splits each value into one list.
        except:
            print("FILE NOT FOUND.")
            self.toplabel_set("Filepath not found.", -1)
            QApplication.restoreOverrideCursor()
            return -1
        
        self.tableBox.clear()
        self.tableBox.setColumnCount(11)
        self.tableBox.setRowCount(len(data))
        self.tableBox.setHorizontalHeaderLabels(["IP Address", "Day", "New Date", "Old Date", "Computer", "User", "Process Variable", "New", "Old", "Min", "Max"])
        self.tableBox.setUpdatesEnabled(False)
        maxline = self.maxlineBox.value()
        if(maxline == 0):
            maxline = len(data)
        a = 0
        b = 0
        self.toplabel_set("Adding data to table...", -1)

        while a < len(data): # splits each line of the data.
            data[a] = data[a].split()

            if(len(data[a]) == 0): # if current item is an empty list, pops item and continues loop.
                data.pop(a)
                continue

            while b < len(data[a]):

                if(b == 2): # turns this index into date 1, then removes redundant data
                    data[a][2] = self.fixup_date(data[a][5] + "-" + data[a][2] + "-" + data[a][3] + " " + data[a][4], 1)
                    for i in range(3):
                        data[a].pop(3)

                if(b == 3): # turns this index into date 2, removes redundant data
                    data[a][3] =  self.fixup_date(data[a][3] + " " + data[a][4], 2)
                    data[a].pop(4)

                self.tableBox.setItem(a, b, QTableWidgetItem(data[a][b])) # creates and sets tablewidgetitem in table for each string

                b += 1

            if(len(data[a]) == 9): # checks for and adds blank items to list
                self.tableBox.setItem(a, 9, QTableWidgetItem("N/A"))
                self.tableBox.setItem(a, 10, QTableWidgetItem("N/A"))

            a += 1
            b = 0
            if(a >= maxline):
                break

        self.tableBox.setRowCount(len(data) if len(data) < maxline else maxline)
        self.tableBox.resizeColumnsToContents()
        self.tableBox.setUpdatesEnabled(True)
        del data
        QApplication.restoreOverrideCursor()
        return("Fileread done.")
# end of LogWindow class.

app = QApplication(sys.argv)
window = LogWindow() # the entire class which was created above
window.show()
app.exec()

#TODO: Make the linebox get used instead of the tablebox after searching.
#TODO: Reorganize the rows, remove week day.
#TODO: Add timer functionality.
#TODO: Options menu for extra configuration.
#TODO: Config file to save default log file and other options.
#TODO: Default sort by new date.