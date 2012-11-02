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

import os
import sys
import Tkinter
import tkMessageBox
import xml.etree.ElementTree as ET
import re

#TODO: add a text box with scrollbars for output and error messages of system command (add a minimum text box size)
#TODO: add an option in XML config file to show or not show the output and error messages

# the name of the configuration file in users home directory
ConfigFileName = os.path.expanduser('~') + '/.commandlinelauncher.xml'

# the default configuration is empty
DefaultConfig = {
                 'TitleString' : 'Command Line Launcher' ,
                 'LabelString' : "Please edit the file %s and rename the script, to match a certain configuration" % ConfigFileName,
                 'Commands'    : [] ,
                 'GridWidth' : 1
} 

# contents of the config file. Will be written, if no config file can be found
ConfigFileDefaultContents = """<?xml version="1.0" encoding="UTF-8" ?>
<CLLConfig>
    <GeneralConfiguration></GeneralConfiguration>
    <SpecialConfigurations>
        <!-- This is the default configuration. Please adapt accordingly -->
        <Configuration name ="CommandLineLauncher">
            <Title>%(TitleString)s</Title>
            <LabelText>%(LabelString)s</LabelText>
            <GridWidth>%(GridWidth)s</GridWidth>
            <CommandList>
                <!-- This is the sytax for command entries:
                <Command text="TEXT"><![CDATA[SHELLCOMMAND]]></Command>
                -->
            </CommandList>
        </Configuration>
    </SpecialConfigurations>
</CLLConfig>
""" % DefaultConfig

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
        button = Tkinter.Button(win, text=com.text, command=(lambda c=com.command: os.system(c)), width=buttonwidth)
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

def errorMessageAndExit(message):
    """Show an error message box and exit"""
    tkMessageBox.showerror("Command Line Launcher", message)    
    exitProgram(1)

def openConfigFile(fileName):
    """open the file, if it doesn't exist, create it, if it doesn't work 
    exit program with error message"""
    try:
        f = open(ConfigFileName,'r')
    except IOError:
        try:
            with open(ConfigFileName,'w') as f:
                f.write(ConfigFileDefaultContents)
            f.close()
            f = open(ConfigFileName,'r')
        except:
            errorMessageAndExit("config File %s cannot be read or written!" % ConfigFileName)
    # here, f should be a valid file handle
    return f

def parseConfigXMLFile(name):
    """
    Read and parse config File ~/.commandlinelauncher.xml with Commands-structure
    return read config or DefaultConfig on error
    """
    f = openConfigFile(ConfigFileName)
    config = {}
    try:
        tree = ET.parse(f)
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
    # here f should be a valid file handle => close it
    f.close()
    
    # return read config or DefaultConfig on error
    if config:
        return config
    else:
        return DefaultConfig

def determineConfigName():
    """determine configuration name according to file name or command line argument"""
    # get config name from file name
    match = re.search('([^/]+).py$', sys.argv[0])
    configName = match.group(1)
    # take config name from argument if given 
    if(len(sys.argv) > 1):
        configName = sys.argv[1]
    return configName

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
    # add the buttons for the system command
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
