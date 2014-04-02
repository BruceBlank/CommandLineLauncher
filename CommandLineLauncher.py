#!/usr/bin/python

"""
This script shows a dialog to start shell commands. 
The definition of the dialog is written in a configuration
file ~/.CommandLineLauncher in the users home directory. 
The configuration to choose will be determined by script
file name or the first command line argument. 
So, you can use the same python script with different 
soft-links to it.   
"""

import Tkinter
# local imports
from MyToolbox import CMyToolbox
from ConfigFileParser import CConfigFileParser
from CommandThread import CCommandThread

#TODO: resize output frame, when application window will be resized
#TODO: group command buttons together

class CCommandLineLauncher(Tkinter.Frame):
    """A class that represents the applications window"""        

    # static variables
    UpdateInterval = 200

    def executeCommand(self, command):
        """ execute the command in shell """
        # dont execute two commands at the same time
        if not self.commandThread or self.commandThread.isRunning():
            return
        
        # disable all buttons in GUI.
        self.buttonsDisabled = True
        for button in self.commandButtons:
            button.config(state="disabled")
        
        # clear text in output frame
        self.outputWindow.delete(1.0, "end")
        
        # set the command and start the thread.
        self.commandThread = CCommandThread()
        self.commandThread.setCommand(command)        
        self.commandThread.start()
        
    def updateGUI(self):
        """ will be called in GUIs update loop. """
        self.master.after(self.UpdateInterval, self.updateGUI)

        # read output and update output frame
        if self.commandThread and self.commandThread.isRunning():
            lines = self.commandThread.dumpOutputLines()
            for line in lines:
                self.outputWindow.insert("end", line)
            self.outputWindow.see("end")

        # maybe enable all buttons in GUI
        if self.buttonsDisabled and self.commandThread and not self.commandThread.isRunning():
            self.buttonsDisabled = False
            for button in self.commandButtons:
                button.config(state="normal")

        
    def calculateButtonWidth(self):
        """calculate the width of a button according to text sizes"""
        textlen = 0
        for com in self.config["Commands"]:
            if textlen < len(com.text):
                textlen = len(com.text)
        return textlen

    def addButtons(self):
        """add buttons to the grid according to the defined commands"""
        col = 0
        row = 1
        for com in self.config['Commands']:
            print com.text
            button = Tkinter.Button(self, text=com.text, command=(lambda c=com.command: self.executeCommand(c)), width=self.buttonwidth)
            button.grid(row=row, column=col, padx=3, pady=3)
            self.commandButtons.append(button)
            col += 1
            if(col==self.config['GridWidth']):
                col = 0
                row += 1
        return row
           
    def toggleOutputWindow(self):
        """ toggle between showing and not-showing the output window. """
        if(self.outputWindowVisible):
            self.outputWindow.grid_remove()
            self.outputWindowVisible = False
        else:
            self.outputWindow.grid()
            self.outputWindowVisible = True
           
    def __init__(self, root, config):
        Tkinter.Frame.__init__(self, root, padx=20, pady=20)
        # define the instance variables
        self.root = root
        self.config = config
        self.buttonwidth = self.calculateButtonWidth()
        self.commandButtons = []
        self.outputWindow = None
        self.outputWindowVisible = True
        self.commandThread = CCommandThread()
        self.buttonsDisabled = False
        """create the dialog and call the main loop"""
        gridwidth = self.config['GridWidth']
        self.root.title(self.config['TitleString'])
        self.root.resizable(0,0)
        self.pack()
        # add a title string to the top
        label = Tkinter.Label(self, text=self.config['LabelString'].decode("string_escape"))
        label.grid(row=0, columnspan=gridwidth, pady=(0, 20))
        # add the buttons for the system command
        nextrow = self.addButtons() + 1
        self.outputWindow = Tkinter.Text(self, width=1, height=15)
        self.outputWindow.grid(row=nextrow, column=0, columnspan=gridwidth, pady=(20, 0), sticky="WENS")
        # show the output window?
        if(config["ShowCommandOutput"]==0):
            self.toggleOutputWindow()
        nextrow += 1
        # add a close-button at left center 
        button = Tkinter.Button(self, text="Close", command=(lambda: CMyToolbox.exitProgram(0)), width=self.buttonwidth)
        button.grid(row=nextrow, column=gridwidth-1, pady=(20, 0))
        # update GUI periodically
        self.master.after(self.UpdateInterval, self.updateGUI)

if __name__ == '__main__':
    parser = CConfigFileParser()
    config = parser.getConfiguration()
    app = CCommandLineLauncher(Tkinter.Tk(), config)
    app.mainloop()
