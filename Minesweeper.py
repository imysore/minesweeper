from tkinter import *
from tkinter import messagebox
import time
import random

class MSCell(Label):
    '''represents a MineSweeper cell'''

    def __init__(self,master,coord,number=0,isBomb=False):
        '''MSCell(master,coord,number) -> MSCell
        creates a new blank MineSweeper cell with (row,column) coord
        Contains number "number" (default is 0), or a bomb (default is False)'''
        Label.__init__(self,master,height=1,width=2,text='',\
                       bg='white',font=('Arial',24),relief=RAISED)
        self.coord = coord     # store coordinate attribute
        self.number = number   # store number attribute
        self.isBomb = isBomb   # store whether the cell contains a bomb
        self.isFlagged = False # store whether the cell is flagged
        self.exposed = False   # store whether the cell is exposed
        # listeners
        self.bind('<Button-1>',self.set_number)
        self.bind('<Button-2>',self.flag)

    def get_coord(self):
        '''MSCell.get_coord() -> tuple
        returns the (row,column) coordinate of the cell'''
        return self.coord

    def get_number(self):
        '''MSCell.get_number() -> int
        returns the number in the cell (0 if empty or bomb)'''
        return self.number

    def is_bomb(self):
        '''MSCell.is_bomb() -> boolean
        returns True if the cell contains a bomb, False if not'''
        return self.isBomb

    def is_flagged(self):
        '''MSCell.is_flagged() -> boolean
        returns True if the cell is flagged, False if not'''
        return self.isFlagged

    def get_background(self):
        '''MSCell.get_background -> str
        returns cell's background'''
        return self['bg']

    def is_exposed(self):
        '''MSCell.is_exposed -> bool
        returns True if the cell is a bomb and has been exposed
        False if not'''
        return self.exposed
    
    def set_number(self,event):
        '''MSCell.set_number(event) -> None
        exposes the cell if the mouse is clicked
        shows red background if bomb
        shows nothing if number is 0
        shows the number if number is not 0'''
        # list of colors
        colormap = ['','blue','darkgreen','red','purple', \
                    'maroon','cyan','black','dim gray']
        # a bomb has been activated
        if self['text'] != "*":
            if self.isBomb:
                self['bg'] = 'red'  # set background color to red
                self['text'] = '*'  # change text to asterick
                self.exposed = True # bomb has been exposed
            else:
                self['bg'] = 'light gray'  # change background to light gray
                self['relief'] = SUNKEN    # change relief to sunken
                # we should show the number
                if self.number != 0:
                    self['text'] = str(self.number)    # set text to number
                    self['fg'] = colormap[self.number] # change color font

    def flag(self,event):
        '''MSCell.flag(event) -> None
        flags/unflags a cell if it has not been exposed'''
        # cell has not been exposed
        if self['bg'] == 'white':
            self.isFlagged = not self.isFlagged  # change isFlagged attribute
            # change text
            if self['text'] == '':
                self['text'] = '*'
            elif self['text'] == '*':
                self['text'] = ''

class MSGrid(Frame):
    '''object for a Minesweeper grid'''

    def __init__(self,master,width,height,numBombs):
        '''MSGrid(master,width,height,numBombs)
        creates a new blank Minesweeper grid
        with dimensions width*height and numBombs bombs'''
        # initialize frame
        Frame.__init__(self,master,bg='black')
        self.grid()
        # store attributes
        self.height = height
        self.width = width
        self.numBombs = numBombs
        self.cells = {}  # dictionary of cells
        self.bombs = []  # list of bombs
        # pick the random bombs
        while len(self.bombs) < numBombs:
            randRow = random.randint(0,height-1)
            randColumn = random.randint(0,width-1)
            if (randRow,randColumn) not in self.bombs:
                self.bombs.append((randRow,randColumn))
        # initialize the cells for the grid
        for row in range(height+1):
            for column in range(width+1):
                coord = (row,column)
                # if coordinate contains a bomb, initialize cell with bomb
                if coord in self.bombs:
                    self.cells[coord] = MSCell(master,coord,isBomb=True)
                # otherwise, initialize cell with number 0
                # we will change this later
                else:
                    self.cells[coord] = MSCell(master,coord,number=0)
        # initialize the actual number for each cell
        for row in range(height):
            for column in range(width):
                coord = (row,column)
                # cell does not contain a bomb
                if not self.cells[coord].is_bomb():
                    self.cells[coord] = MSCell(master,coord,number=self.find_bombs_adjacent(coord))
                self.cells[coord].grid(row=coord[0],column=coord[1])
        self.status = self.cells.values()   # store status of cells
        self.oldCellList = []               # cells that have already been clicked on
        # listeners
        self.master.bind("<Button-1>",self.check_for_bomb_or_expose)
        self.master.bind("<Button-2>",self.update_label)
        # labels for flags left
        Label(master,text="Flags left: ",font=('Arial',24)).grid(row=self.height+1,column=self.width//2-3,columnspan=4)
        self.tracker = Label(master,text=self.numBombs,font=('Arial',24))
        self.tracker.grid(row=self.height+1,column=self.width//2,columnspan=2)

    def find_bombs_adjacent(self,coord):
        '''MSGrid.find_bombs_adjacent(coord)
        finds and returns the number of bombs adjacent to the square
        coord is the coordinate shown'''
        count = 0
        # loop through adjacent cells
        for i in range(-1,2):
            for j in range(-1,2):
                currentCoord = (coord[0]+i,coord[1]+j)  # store current coordinate
                # make sure coordinate is valid and a bomb
                if currentCoord in self.cells and self.cells[currentCoord].is_bomb():
                    count += 1
        return count

    def update_label(self,event):
        '''MSGrid.update_label()
        updates the number of bombs subtracted by the
        number of flagged squares'''
        flagCount = 0
        # loop through cells, see how many are flagged
        for cell in self.cells:
            if self.cells[cell].is_flagged():
                flagCount += 1
        # update label
        self.tracker['text'] = self.numBombs - flagCount
        self.check_for_win()    # see if player has won by clicking last flag

    def check_for_bomb_or_expose(self,event):
        '''MSGrid.check_for_bomb_or_expose()
        checks for a bomb
        if none, auto-expose squares without number'''
        count = 0
        for item in self.status:
            # new cell has been visited
            if item.get_background() != 'white' and item not in self.oldCellList:
                self.oldCellList.append(item)   # add cell to item
                newCoord = item   # store coordinate
                count += 1
        # check if player has lost
        for cell in self.cells:
            # bomb has been pressed
            if self.cells[cell].is_exposed():
                # show error
                messagebox.showerror('Minesweeper','KABOOM! You lose.',parent=self)
                # show remaining bombs
                for bomb in self.bombs:
                    self.cells[bomb].set_number(self.cells[cell])
                # check if player misflagged cells
                for cell in self.cells.values():
                    if cell.is_flagged() and not cell.is_bomb():
                        cell['text'] = 'X'
                self.unbind_everything()
                return
        # if not bomb, auto-expose squares
        if count != 0:
            self.auto_expose(newCoord.get_coord())
        self.check_for_win()    # check if player won

    def auto_expose(self,coord):
        '''MSGrid.auto_expose(coord)
        auto-exposes cells next to cell given by coordinate'''
        if coord not in self.oldCellList:
            self.oldCellList.append(coord)
            # stop if cell is a bomb
            if self.cells[coord].is_bomb():
                return
            else:
                if self.cells[coord].get_number() == 0:
                    # set number
                    self.cells[coord].set_number(self.cells[coord])
                    # recursive steps for adjacent cells
                    if coord[0] > 0:
                        self.auto_expose((coord[0]-1,coord[1]))
                    if coord[0] < self.height:
                        self.auto_expose((coord[0]+1,coord[1]))
                    if coord[1] > 0:
                        self.auto_expose((coord[0],coord[1]-1))
                    if coord[1] < self.width:
                        self.auto_expose((coord[0],coord[1]+1))
                else:
                    self.cells[coord].set_number(self.cells[coord])

    def check_for_win(self):
        '''MSGrid.check_for_win()
        checks if a player has won'''
        # loop through all cells
        for i in range(self.height):
            for j in range(self.width):
                # if there are still cells remaining
                if self.cells[(i,j)].get_background() in ['white','red']:
                    # cell is not flagged
                    if not self.cells[(i,j)].is_flagged():
                        return  # player has not won
        # positive number of flags, then player has won
        if self.tracker['text'] >= 0:
            messagebox.showinfo('Minesweeper','Congratulations -- you won!',parent=self)
        self.unbind_everything()
        
    def unbind_everything(self):
        '''MSGrid.unbind_everything()
        unbinds everything if the player wins/loses'''
        # unbind each cell
        for i in range(self.height):
            for j in range(self.width):
                self.cells[(i,j)].unbind("<Button-1>")
                self.cells[(i,j)].unbind("<Button-2>")
        # unbind frame
        self.master.unbind("<Button-1>")
        self.master.unbind("<Button-2>")


def play_minesweeper(width,height,numBombs):
    '''play_minesweeper()
    plays a game of minesweeper
    on a width * height board with numBombs bombs'''
    root = Tk()
    root.title('Minesweeper')
    grid = MSGrid(root,width,height,numBombs)
    root.mainloop()

play_minesweeper(9, 9, 15)
