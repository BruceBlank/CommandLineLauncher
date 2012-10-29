#!/usr/bin/python

import os
import Tkinter
import xml.etree.ElementTree as ET

#TODO: add a text box instead of a label for the LabelString (centered, multiline text)
#TODO: add a text box with scrollbars for output and error messages of system command (add a minimum text box size)
#TODO: add command line arguments to Python script: Which configuration to parse
#TODO: parse XML-file: Configuration according to command line or Python-script-name


# the name of the configuration file in users home directory
ConfigFileName = '.commandlinelauncher.xml'

class CommandDescription:
    def __init__(self, text, command):
        self.text = text
        self.command = command

# this can be changed:
GlobalConfig = {
          'TitleString' : 'Ultra Remote Control' ,
          'LabelString' : 'What do you want to do?',
          'Commands'    : [
                           CommandDescription('Wake Up', 'sudo etherwake 00:1C:85:40:24:E3') ,
                           CommandDescription('Shutdown', 'ssh ultra@ultra sudo shutdown -h now') ,
                           CommandDescription('Restart VDR', 'ssh ultra@ultra sudo /etc/init.d/vdr restart') ,
                           CommandDescription('Bark', 'play /usr/share/sounds/gnome/default/alerts/bark.ogg') ,
                           ] ,
          'GridWidth' : 3
}

# the default configuration is empty
DefaultConfig = {
                 'TitleString' : 'Command Line Launcher' ,
                 'LabelString' : 'Please edit the file ~/.commandlinelauncher and rename the script, to match a certain configuration',
                 'Commands'    : [] ,
                 'GridWidth' : 1
} 

def exitProgram(status):
    """exit this Python script"""    
    Tkinter.sys.exit(status)

def addButtons(win, config, buttonwidth):
    """add buttons to the grid according to the defined commands"""
    col = 0
    row = 1
    for com in config['Commands']:
        syscom = (lambda: os.system(com.command))
        Tkinter.Button(win, text=com.text, command=syscom, width=buttonwidth).grid(row=row, column=col, padx=3, pady=3)
        col += 1
        if(col==config['GridWidth']):
            col = 0
            row += 1
    return row
        
def calculateButtonWidth(commands):
    """calculate the width of a button according to text sizes"""
    textlen = 0
    for com in commands:
        if textlen < len(com.text):
            textlen = len(com.text)
    return textlen

def parseConfigXMLFile():
    """Really Read and parse config File ~/.commandlinelauncher.xml with Commands-structure"""
    # TODO: Really Read and parse XML-File with Commands-structure
    root = ET.fromstring('<Data></Data>') 
    #return DefaultConfig
    return GlobalConfig

def showDialog(config):
    """create the dialog and call the main loop"""
    buttonwidth = calculateButtonWidth(config['Commands'])
    gridwidth = config['GridWidth']
    # initialize dialog
    root = Tkinter.Tk()
    root.title(config['TitleString'])
    win = Tkinter.Frame(padx=20, pady=20)
    win.pack()
    # add a title string to the top
    Tkinter.Label(win, text=config['LabelString']).grid(row=0, columnspan=gridwidth, pady=(0,20))
    # add the buttons for teh system command
    lastrow = addButtons(win, config, buttonwidth)
    # add a close-button
    button = Tkinter.Button(win, text="Close", command=(lambda: exitProgram(0)), width=buttonwidth)
    # center close-button (according to odd/even gridwidth)
    if(gridwidth & 1):
        button.grid(row=lastrow+1, column=gridwidth/2, pady=(20,0), columnspan=1)
    else:
        button.grid(row=lastrow+1, column=gridwidth/2-1, pady=(20,0), columnspan=2)
    win.mainloop()

if __name__ == '__main__':    
    showDialog(parseConfigXMLFile())
