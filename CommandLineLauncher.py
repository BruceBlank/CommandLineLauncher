#!/usr/bin/python

import os
import Tkinter
import xml.etree.ElementTree as ET

#TODO: add a text box instead of a label for the LabelString (centered, multiline text)
#TODO: add a text box with scrollbars for output and error messages of system command (add a minimum text box size)
#TODO: add command line arguments to Python script: Which configuration to parse


# the name of the configuration file in users home directory
ConfigFileName = os.path.expanduser('~') + '/.commandlinelauncher.xml'

# the default configuration is empty
#TODO: Output: Maybe an error in configuration file syntax? 
DefaultConfig = {
                 'TitleString' : 'Command Line Launcher' ,
                 'LabelString' : "Please edit the file %s and rename the script, to match a certain configuration" % ConfigFileName,
                 'Commands'    : [] ,
                 'GridWidth' : 1
} 

class CommandDescription:
    def __init__(self, text, command):
        self.text = text
        self.command = command

def exitProgram(status):
    """exit this Python script"""    
    Tkinter.sys.exit(status)

def addButtons(win, config, buttonwidth):
    """add buttons to the grid according to the defined commands"""
    col = 0
    row = 1
    for com in config['Commands']:
        #TODO: using bound methods for callback!!!
        button = Tkinter.Button(win, text=com.text, command=(lambda: os.system(com.command)), width=buttonwidth)
        button.grid(row=row, column=col, padx=3, pady=3)
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

def parseConfigXMLFile(name):
    """
    Read and parse config File ~/.commandlinelauncher.xml with Commands-structure
    return read config or DefaultConfig on error
    """
    config = {}
    try:
        tree = ET.parse(ConfigFileName)
        root = tree.getroot()
        # at the moment, no general configuration items defined
        # find first matching configuration within SpecialConfiguration tag
        matchingConfig = None
        for c in root.findall("./SpecialConfigurations/Configuration"):
            if(c.attrib['name'] == name):
                matchingConfig=c
                break
        if(matchingConfig is not None):
            # matching config found, set options accordingly
            config['TitleString'] = matchingConfig.find('Title').text
            config['LabelString'] = matchingConfig.find('LabelText').text
            config['GridWidth'] = int(matchingConfig.find('GridWidth').text)
            comLst = []
            for c in matchingConfig.findall("./CommandList/Command"):
                comLst.append(CommandDescription(c.attrib['text'], c.text))
            config['Commands'] = comLst
    except:
        config = {}
    # return read config or DefaultConfig on error
    if config:
        return config
    else:
        return DefaultConfig

def determineConfigName():
    #TODO: really determine active configuration name according to file name or command line argument
    #return 'UltraRemote'
    return 'TestLauncher'

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
    configName = determineConfigName()
    config = parseConfigXMLFile(configName)
    showDialog(config)
