import sys # imports system module
from PyQt5 import QtCore # imports qtcore module
from PyQt5.QtCore import QSize, Qt, QStringListModel, QModelIndex, QVariant # imports qsize and qt classes
#from PyQt5.QtCore import QVector
from PyQt5.QtWidgets import QApplication, QCheckBox, QFileDialog, QMainWindow, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget # imports.. a lot of widget classes

class LogWindow(QMainWindow): # The entire window.
    def __init__(self): # initializes all of the values
        super().__init__() # this initializes it with the mainwindow
        #self.stinky = QVector()
        self.version = "v0.6.0" # program version.
        self.filepath = "data.txt" # file location, also used to display
        self.setWindowTitle("pyLogViewer " + self.version + " - " + self.filepath) # window name
        self.sortDown = True # always sort columns descending by default
        self.lastIndex = 0 # last selected column, 0 is default
        self.searchlist = -1 # contains coordinates of current search matches
        self.lastsearch = -1 # the last search, as a string. used for comparison to current search
        self.searchindex = -1 # which position in the searchlist the user is at
        self.lastlight = False # allows you to click highlight again to view your current place
        self.maxline = 5000000 # maximum amount of lines to read.

        self.label = QLabel("Initializing...") # shows text.
        
        self.tableBox = QTableWidget() # table which shows all data
        self.tableBox.setEditTriggers(QTableWidget.NoEditTriggers) # prevents editing of table items
        self.fileRead() # most important line. sorts the data and passes it to setdatatable and sorts it further and puts it in the table.
        self.tableBox.horizontalHeader().sectionClicked.connect(self.tablesort) # allows for sorting via header click

        self.inputBox = QLineEdit() # edit line. lets you edit text in the line.
        self.inputBox.installEventFilter(self) # checks for enters

        self.caseCheck = QCheckBox("Case sensitive?") # toggles searches being case sensitive
        self.caseCheck.stateChanged.connect(self.clearsearch) # clears search to cause the next one to re-evaluate list with new conditions

        self.buttonHighlight = QPushButton("Highlight All") # searches results and highlights all (slow)
        self.buttonHighlight.clicked.connect(lambda : self.searchtable(0)) # passes zero to searchtable method for highlight mode

        self.buttonSprev = QPushButton("Find Prev") # finds results. browses from greatest to least
        self.buttonSprev.clicked.connect(lambda : self.searchtable(-1)) # lambda makes small functions. can't connect a method with an argument so this is needed
        self.buttonSnext = QPushButton("Find Next") # finds results. browses from least to greatest
        self.buttonSnext.clicked.connect(lambda : self.searchtable(1)) # passes direction to searchtable method

        self.buttonFile = QPushButton("Open File") # button. it buttons.
        self.buttonFile.clicked.connect(self.filePrompt) # opens a file prompt when the button is clicked

        self.setMinimumSize(QSize(500, 300)) # i truly wonder what "setMinimumSize" does.
        self.resize(900, 500) # window   size

        self.bottombar = QHBoxLayout() # horizontal layout, allows multiple widgets going horizontally. useful for the search box and buttons
        self.bottombar.insertWidget(1, self.buttonFile) # button to import file
        self.bottombar.insertWidget(2, self.inputBox) # box where you type
        self.bottombar.insertWidget(3, self.buttonHighlight) # button that highlights results
        self.bottombar.insertWidget(4, self.buttonSprev) # button that searches and goes back a result
        self.bottombar.insertWidget(5, self.buttonSnext) # button that searches and goes forwards a result
        self.bottombar.insertWidget(6, self.caseCheck) # checkbox that toggles case sensitivity

        self.toplabel_set("Click a header to sort, or use the box to search.", self.tableBox) # sets the message after initialization to prompt user action

        self.layout = QVBoxLayout() # object containing the vertical layout, not window
        self.layout.addWidget(self.label) # text from the edited line
        self.layout.addWidget(self.tableBox) # table showing data
        self.layout.addLayout(self.bottombar) # the entire horizontal search layout. they can be nested... how useful!

        container = QWidget() # widget containing multiple laid out widgets
        container.setLayout(self.layout) # give it the layout!~

        self.setCentralWidget(container) # makes the container the central widget... so you can see anything

    def clearsearch(self): # clears the search variables. prevents issues and forces next search to occur
        self.searchlist = -1
        self.searchindex = -1
        self.lastsearch = -1

    def searchtable(self, dir): # creates list of all occurrences of specified value and subsequently proceeds through it
        search = self.inputBox.text() # the current input from the input box widget

        # below code is executed on repeat searches
        if(self.lastsearch == search and (dir != 0 or self.lastlight)): # executed if its a repeat of the same search, AND either: the current move isn't a highlight OR the last move was a highlight 
            self.searchindex += (dir) # moves selection in direction. rhymes
            if(self.searchindex >= len(self.searchlist)): # index above range handling
                self.searchindex = 0 # wrap around effect
            if(self.searchindex < 0): # index below range handling
                self.searchindex = len(self.searchlist) - 1 # wrap around effect
            self.toplabel_set("Viewing " + str(self.searchindex + 1) + " of " + str(len(self.searchlist)) + ' results for "' + search + '".', self.tableBox) # which result you're viewing out of total
            self.tableBox.setCurrentCell(self.searchlist[self.searchindex][0], self.searchlist[self.searchindex][1]) # highlight and go to new selection
            self.lastlight = False # the last search was NOT a highlight, because this code selects one only.
            return # exit the method.
        elif(self.lastsearch == search and dir == 0): # else if the search is the same as last time AND the last move wasn't a highlight (lastmove should always not be highlight)
            QApplication.setOverrideCursor(Qt.WaitCursor) # loading cursor because this can take a while
            #self.searchindex = 0
            z = 0
            while z in range(len(self.searchlist)): # iterates thru searchlist coords
                self.tableBox.item(self.searchlist[z][0], self.searchlist[z][1]).setSelected(True) # ...and highlights everything WITHOUT making an entire new list
                #self.tableBox.setCurrentCell(self.searchlist[z][0], self.searchlist[z][1])
                #print(str(self.searchlist[z][0]) + ", " + str(self.searchlist[z][1]))
                z += 1
            
            self.toplabel_set("Viewing " + str(self.searchindex + 1) + " of " + str(len(self.searchlist)) + ' results for "' + search + '". Highlighting.', self.tableBox) # tells user its highlighted
            self.lastlight = True # the last move WAS a highlight, this code does that.
            QApplication.restoreOverrideCursor() # normal cursor again, huzzah!
            return # exit the method.

        # below code is executed on new searches
        self.toplabel_set("Searching...", self.tableBox) # let user know theyre gonna have to wait a bit
        QApplication.setOverrideCursor(Qt.WaitCursor) # loading cursor with same purpose
        self.searchlist = [] # the list... is an empty
        if(search == ""): # returns if its nothing.
            self.toplabel_set("No search value entered.", self.tableBox) # does this if you try to search nothing for some reason
            QApplication.restoreOverrideCursor() # gets the load cursor out of here
            return # exit the method.
        
        row = 0 # loop var for table row
        highlightfirst = True # highlight mode will send the user to the first found value. just so they see a result, in case there are few.

        self.tableBox.clearSelection() # removes selections in table widget
        while row in range(self.tableBox.rowCount()): # goes through every row of the table.
            column = 0 # loop var for table column
            while column in range(self.tableBox.columnCount()): # goes through every column of the table.
                if((self.tableBox.item(row, column).text().find(search) != -1) or (self.tableBox.item(row, column).text().lower().find(search.lower()) != -1 and  not self.caseCheck.isChecked())): # if the string was found
                    self.searchlist.append([row, column])
                    if(dir == 0): # if triggered by pressing enter, shows all results highlighted
                        if highlightfirst:
                            self.tableBox.setCurrentCell(self.searchlist[0][0], self.searchlist[0][1]) # highlight and go to it
                            highlightfirst = False
                        self.tableBox.item(row, column).setSelected(True)
                    #print("found at " + str(row) + ", " + str(column))
                    #self.toplabel_set("Found " + str(len(self.searchlist)) + " items...", self.tableBox)
                column += 1
            row += 1

        if(len(self.searchlist) > 0): # goes to the first or last value if the searchlist has results.
            self.searchlist = tuple(map(tuple, self.searchlist))
            if(dir == 0): # if triggered by enter, only display the total number
                self.lastlight = True
                self.searchindex = 0
                self.toplabel_set("Viewing all " + str(len(self.searchlist)) + ' results for "' + search + '".', self.tableBox)
            else: # otherwise, go to the first result, display the current item and set the search index.
                self.lastlight = False
                _num = -1 if dir == -1 else 0
                self.tableBox.setCurrentCell(self.searchlist[_num][0], self.searchlist[_num][1]) # highlight and go to it
                self.searchindex = 0
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
        return super().eventFilter(obj, event) # RESEARCH THIS

    def reinit(self): # REINITIALIZATION!!! Brings everything to zero and reads a new file.
        self.sortDown = True # always sort descending by default
        self.lastIndex = 0 # last selected column, 0 is default
        self.clearsearch() # clears the search variables
        try: # if the code fails, the exception is handled.
            self.fileRead() # adds cleaned up data array to the data table
        except:
            self.tableBox.clear() # empty the box
            #del self.model
            #self.model = QStringListModel()
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

        #try: # checks if file even exists otherwise it exits and nothing ever happens
        with(open(self.filepath, 'r')) as logfile:
                data = logfile.read()

                data = data.split("\n") # removes blanks between lines and splits each value into one list.

                #if(len(data) > self.maxline): # cuts list off at specified line
                #    data = data[:self.maxline]
        '''except:
            print("FILE NOT FOUND.")
            self.inputBox.clear()
            self.toplabel_set("Filepath not found.", -1)
            #self.layout.update()
            QApplication.restoreOverrideCursor()
            return -1'''
        #print(data) # debug print.
        
        self.tableBox.clear()
        self.tableBox.setColumnCount(11)
        self.tableBox.setRowCount(len(data))
        self.tableBox.setHorizontalHeaderLabels(["IP Address", "Day", "Date1", "Date2", "Computer", "User", "Process", "New", "Old", "Min", "Max"])
        self.tableBox.setUpdatesEnabled(False)
        a = 0
        b = 0
        self.toplabel_set("Adding data to table...", -1)

        while a < len(data): # splits each line of the data.
            data[a] = data[a].split()

            if(len(data[a]) == 0): # if current item is an empty list, pops item and continues loop.
                #print("oof" + str(data[a])) # debug print.
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

                #print("[" + str(data[a][b]), end = "] ") # debug print.
                self.tableBox.setItem(a, b, QTableWidgetItem(data[a][b])) # creates and sets tablewidgetitem in table for each string

                b += 1

            if(len(data[a]) == 9): # checks for and adds blank items to list
                self.tableBox.setItem(a, 9, QTableWidgetItem("N/A"))
                self.tableBox.setItem(a, 10, QTableWidgetItem("N/A"))

            a += 1
            b = 0
            if(a >= self.maxline):
                break
            #print() # debug print.

        #print(data) # debug print.

        self.tableBox.setRowCount(len(data) if len(data) < self.maxline else self.maxline)
        self.tableBox.resizeColumnsToContents()
        self.tableBox.setUpdatesEnabled(True)
        del data
        QApplication.restoreOverrideCursor()
        #return("Fileread done.") # debug print.
# end of LogWindow class.

app = QApplication(sys.argv)
window = LogWindow() # the entire class which was created above
window.show()
app.exec()