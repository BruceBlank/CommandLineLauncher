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

import sys
import Tkinter
# local imports
from MyToolbox import CMyToolbox
from ConfigFileParser import CConfigFileParser
import CommandThread

#TODO: remove that:
import threading
import subprocess

#TODO: stream standard output and standard error of system command to text boxes (use subprocess.popen)
#TODO: separate GUI and processing into different threads (use subprocess.popen)
#TODO: disable all buttons while shell command executes  
#TODO: output text boxes can be shown or hidden with buttons and/or with config file entry

class CCommandLineLauncher(Tkinter.Frame):
    """A class that represents the applications window"""        

    # static variables
    UpdateInterval = 200

    def commandThread(self, command):
        #FORTESTING:
        #command="echo 1; sleep 1; echo 2; sleep 2; echo 3"
        self.proc=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # output one line from the shell-command
        #TODO: output stderr and stdout in output frame
        #TODO: Dont wait, if there is no line 
        while self.proc is not None and self.proc.poll() is None:
            sys.stdout.write(".")
            sys.stdout.flush()
            line = self.proc.stdout.readline()
            sys.stdout.write(line)
            sys.stdout.flush()            
        #for i in range(10):
        #    print i
        #    time.sleep(0.5)

    def executeCommand(self, command):
        #TODO: dont use self.proc here, but special variables shared with commandThread: threading.Lock()
        if self.proc is not None:
            return
       
        # disable all buttons in GUI.
        for button in self.commandButtons:
            button.config(state="disabled")
        
        #FORTESTING
        tt1 = threading.Thread(target=self.commandThread, args=(command,))
        tt1.start()
        
    def updateGUI(self):
        self.master.after(self.UpdateInterval, self.updateGUI)

        #TODO: dont use self.proc here, but special variables shared with commandThread: threading.Lock()

        # test if the subprocess has finished    
        if self.proc is not None and self.proc.poll() is not None:    
            self.proc = None
            # enable all buttons in GUI.
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
        if(self.outputWindowVisible):
            self.errWindow.grid_remove()
            self.outputWindowVisible = False
        else:
            self.errWindow.grid()
            self.outputWindowVisible = True
           
    def __init__(self, master, config):
        Tkinter.Frame.__init__(self, master, padx=20, pady=20)
        # define the instance variables
        self.master = master
        self.config = config
        self.buttonwidth = self.calculateButtonWidth()
        self.commandButtons = []
        self.errWindow = None
        self.outWindow = None
        self.outputWindowVisible = True
        self.proc = None
        """create the dialog and call the main loop"""
        gridwidth = self.config['GridWidth']
        self.pack()
        # add a title string to the top
        label = Tkinter.Label(self, text=self.config['LabelString'].decode("string_escape"))
        label.grid(row=0, columnspan=gridwidth, pady=(0, 20))
        # add the buttons for the system command
        nextrow = self.addButtons() + 1
        # add text boxes and labels for cout and cerr of system commands 
        label = Tkinter.Label(self, text='Standard Output')
        label.grid(row=nextrow, column=0, columnspan=gridwidth, pady=(20, 0), sticky="NW")
        nextrow += 1
        self.errWindow = Tkinter.Text(self, width=1, height=10)
        self.errWindow.grid(row=nextrow, column=0, columnspan=gridwidth, pady=(20, 0), sticky="WENS")
        # show the output window?
        if(config["ShowCommandOutput"]==0):
            self.toggleOutputWindow()
        nextrow += 1
        #TODO: maybe show a STDERR-Textbox
        # add a close-button and center 
        button = Tkinter.Button(self, text="Close", command=(lambda: CMyToolbox.exitProgram(0)), width=self.buttonwidth)
        button.grid(row=nextrow, column=0, pady=(20, 0), columnspan=gridwidth)
        # update GUI periodically
        self.master.after(self.UpdateInterval, self.updateGUI)

if __name__ == '__main__':
    parser = CConfigFileParser()
    config = parser.getConfiguration()
    app = CCommandLineLauncher(Tkinter.Tk(), config)
    app.mainloop()
