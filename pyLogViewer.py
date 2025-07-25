import sys, time # imports system and time modules
from PyQt5 import QtCore # imports qtcore module
from PyQt5.QtCore import QSize, Qt # imports qsize and qt classes
from PyQt5.QtWidgets import QApplication, QSpinBox, QCheckBox, QFileDialog, QMainWindow, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget # imports.. a lot of widget classes

class LogWindow(QMainWindow): # The window class
    def __init__(self): # initializes class values
        super().__init__() # initializes it with mainwindow
        self.version = "v0.5.6"
        self.filepath = "data.txt"
        self.setWindowTitle("pyLogViewer " + self.version + " - " + self.filepath)
        self.sortDown = True # always sort columns descending by default
        self.lastIndex = 0 # last selected column, 0 is default
        self.searchlist = -1 # contains coordinates of current search matches
        self.lastsearch = -1 # the last search, as a string. used for comparison to current search
        self.searchindex = -1 # which position in the searchlist the user is at
        self.lastlight = False # allows you to click highlight again to view your current place

        self.label = QLabel("Initializing...")
        
        self.refreshLabel = QLabel("Seconds to refresh:")
        self.refreshBox = QSpinBox() # editable line, contains search value

        self.maxLabel = QLabel("Max lines:")
        self.maxlineBox = QSpinBox() # editable line, contains search value
        self.maxlineBox.setMaximum(1000000)
        self.maxlineBox.setSingleStep(10000)
        self.maxlineBox.setValue(150000) # maximum amount of lines to read
        self.maxlineBox.setGroupSeparatorShown(True)

        self.tableBox = QTableWidget() # table, contains and shows data
        self.tableBox.setEditTriggers(QTableWidget.NoEditTriggers) # prevents editing of table items
        self.fileRead() # sorts the data and passes it to tablebox
        self.tableBox.horizontalHeader().sectionClicked.connect(self.tablesort) # allows for sorting via header click

        self.inputBox = QLineEdit() # editable line, contains search value
        self.inputBox.installEventFilter(self) # checks for enter presses

        self.caseCheck = QCheckBox("Case sensitive?")
        self.caseCheck.stateChanged.connect(self.clearsearch) # clears search so the next one re-evaluates the list with new conditions

        self.buttonHighlight = QPushButton("Highlight All") # searches results and highlights all (slow)
        self.buttonHighlight.clicked.connect(lambda : self.searchtable(0)) # passes direction to searchtable method. zero is highlight mode

        self.buttonSprev = QPushButton("Find Prev") # prev result of search
        self.buttonSprev.clicked.connect(lambda : self.searchtable(-1)) # can't connect a method with an argument so lambda is needed
        self.buttonSnext = QPushButton("Find Next") # next result of search
        self.buttonSnext.clicked.connect(lambda : self.searchtable(1))

        self.buttonFile = QPushButton("Open File")
        self.buttonFile.clicked.connect(self.filePrompt) # opens a file prompt when the button is clicked

        self.setMinimumSize(QSize(510, 200))
        self.resize(900, 500)

        self.bottombar = QHBoxLayout() # horizontal layout, allows multiple widgets going horizontally. used for the search box and buttons
        self.bottombar.insertWidget(1, self.buttonFile)
        self.bottombar.insertWidget(2, self.inputBox)
        self.bottombar.insertWidget(3, self.buttonSprev)
        self.bottombar.insertWidget(4, self.buttonSnext)
        self.bottombar.insertWidget(5, self.buttonHighlight)
        self.bottombar.insertWidget(6, self.caseCheck)

        self.topbar = QHBoxLayout()
        self.topbar.insertWidget(1, self.label)
        self.topbar.addStretch(2)
        self.topbar.insertWidget(3, self.maxLabel)
        self.topbar.insertWidget(4, self.maxlineBox)
        self.topbar.insertWidget(5, self.refreshLabel)
        self.topbar.insertWidget(6, self.refreshBox)

        self.toplabel_set("Click a header to sort, or use the box to search.", self.tableBox)

        self.layout = QVBoxLayout() # object containing the vertical layout
        self.layout.addLayout(self.topbar)
        self.layout.addWidget(self.tableBox)
        self.layout.addLayout(self.bottombar) # the entire horizontal search layout. they can be nested... how useful!

        container = QWidget() # widget containing multiple laid out widgets
        container.setLayout(self.layout) # give it the layout!~

        self.setCentralWidget(container) # makes the container the central widget

    def clearsearch(self): # clears the search variables. prevents issues and forces next search to occur
        self.searchlist = -1
        self.searchindex = -1
        self.lastsearch = -1
        self.lastlight = False

    def searchtable(self, dir): # creates list of all occurrences of specified value and subsequently proceeds through it
        search = self.inputBox.text() # the current input from the input box widget

        if(search == None or search == ""):
            self.toplabel_set("No search value entered.", self.tableBox) # does this if you try to search nothing for some reason
            return # exit the method.

        # executed on repeat searches. it moves you to the next value in the selected direction. Direction 0 is a highlight, and repeating a highlight selects only cur value.
        if(self.lastsearch == search and (dir != 0 or self.lastlight)): # executed if its a repeat of the same search, AND either: the current move isn't a highlight OR the last move was a highlight 
            self.searchindex += (dir) # moves selection in direction. rhymes

            if(self.searchindex not in range(len(self.searchlist))):
                self.searchindex = 0 if dir != -1 else len(self.searchlist) - 1

            self.toplabel_set("Viewing " + str(self.searchindex + 1) + " of " + str(len(self.searchlist)) + ' results for "' + search + '".', self.tableBox) # result you're viewing out of total
            self.tableBox.setCurrentItem(self.searchlist[self.searchindex]) # highlight and go to new selection
            self.lastlight = False # the last search was NOT a highlight, because this code only selects one.
            return # exit the method.
        elif(self.lastsearch == search and dir == 0): # else if the search is the same as last time AND the last move wasn't a highlight (the lastmove should always not be highlight here)
            QApplication.setOverrideCursor(Qt.WaitCursor)

            for i in range(len(self.searchlist)): # iterates thru searchlist coords
                self.searchlist[i].setSelected(True) # ...and highlights everything WITHOUT making an entire new list
                #self.tableBox.setCurrentItem(self.searchlist[i]) # this sets current position every single highlight. inefficient.

            self.toplabel_set("Viewing " + str(self.searchindex + 1) + " of " + str(len(self.searchlist)) + ' results for "' + search + '". Highlighting.', self.tableBox) # tells user its highlighted
            self.lastlight = True # the last move WAS a highlight
            QApplication.restoreOverrideCursor()
            return

        # executed on new searches, sets the result list and initial position.
        self.toplabel_set("Searching...", self.tableBox)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        if(not self.caseCheck.isChecked()): # flags to determine case sensitivity
            flags = Qt.MatchFlag.MatchContains
        else:
            flags = Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchCaseSensitive

        self.tableBox.clearSelection() # removes selections in table widget
        self.searchlist = self.tableBox.findItems(search, flags) # puts all items from table into list

        if(len(self.searchlist) > 0): # goes to the first or last value if the searchlist has results.
            self.searchindex = 0 if dir != -1 else len(self.searchlist) - 1
            self.tableBox.setCurrentItem(self.searchlist[0 if dir == 1 else dir]) # go to the first result

            if(dir == 0):
                self.lastlight = True
                for i in range(len(self.searchlist)):
                    self.searchlist[i].setSelected(True)
                self.toplabel_set("Viewing all " + str(len(self.searchlist)) + ' results for "' + search + '".', self.tableBox)
            else:
                self.lastlight = False
                self.toplabel_set("Viewing " + str(self.searchindex + 1) + " of " + str(len(self.searchlist)) + ' results for "' + search + '".', self.tableBox)
            
            self.lastsearch = search 
        else:
            self.toplabel_set('No results for "' + search + '".', self.tableBox)

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
        self.clearsearch() # clears the search variables
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

    def tablesort(self, logicalIndex): # sorts the selected column when... a column header is selected.
        self.toplabel_set("Sorting...", self.tableBox) # loading message you know the drill by now
        QApplication.setOverrideCursor(Qt.WaitCursor) # loading cursor.
        headerTxt = self.tableBox.horizontalHeaderItem(logicalIndex).text() # the header text to show later
        if(logicalIndex != self.lastIndex): # checks if this index is the same as the last one sorted
            self.sortDown = True # if not, it will always start sorted descending
            self.lastIndex = logicalIndex # sets the last index to this one
        else: # if so, it will sort the opposite of last time
            self.sortDown = not self.sortDown # yeah. inversion
        
        self.tableBox.sortItems(logicalIndex, self.sortDown) # sorts the items at specified index
        self.toplabel_set("Sorting " + headerTxt + (" descending" if self.sortDown else " ascending"), self.tableBox) # tells user how its sorted

        self.clearsearch() # clears the search variables, they will be incorrect otherwise
        QApplication.restoreOverrideCursor() # no more loading cursor.

    def toplabel_set(self, action, table): # sets the top label to all sorts of things.
        if(table == -1): # -1 replaces the table in some instances to avoid displaying row count
            self.label.setText("Rows: N/A\n" + action) # yeah.
        else: # otherwise
            self.label.setText("Rows: " + str(self.tableBox.rowCount()) + "\n" + action) # it's just the row count !
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
            self.inputBox.clear()
            self.toplabel_set("Filepath not found.", -1)
            QApplication.restoreOverrideCursor()
            return -1
        
        self.tableBox.clear()
        self.tableBox.setColumnCount(11)
        self.tableBox.setRowCount(len(data))
        self.tableBox.setHorizontalHeaderLabels(["IP Address", "Day", "Date1", "Date2", "Computer", "User", "Process", "New", "Old", "Min", "Max"])
        self.tableBox.setUpdatesEnabled(False)
        maxline = self.maxlineBox.value()
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

# TODO: limit "highlight all" to only highlight the nearest thousand or so values.