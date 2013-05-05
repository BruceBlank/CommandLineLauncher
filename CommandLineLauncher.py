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
import threading

#TODO: stream standard output and standard error of system command to text boxes (use subprocess.popen)
#TODO: separate GUI and processing into different threads (use subprocess.popen)
#TODO: disable all buttons while shell command executes  
#TODO: output text boxes can be shown or hidden with buttons and/or with config file entry

class CHelper:
    @staticmethod        
    def exitProgram(status):
        """exit this Python script"""    
        Tkinter.sys.exit(status)

    @staticmethod
    def errorMessageAndExit(message):
        """Show an error message box and exit"""
        tkMessageBox.showerror("Command Line Launcher", message)    
        CHelper.exitProgram(1)

class CCommandDescription:
    def __init__(self, text, command):
        self.text = text
        self.command = command

class CConfigFileParser:
    """a class to hold config file stuff """

    # the name of the configuration file in users home directory
    DefaultConfigFileName = os.path.expanduser('~') + '/.commandlinelauncher.xml'

    # the default configuration is empty
    DefaultConfig = {
                     'TitleString' : 'Command Line Launcher' ,
                     'LabelString' : "Please edit the file %s and rename the script, to match a certain configuration" % DefaultConfigFileName,
                     'Commands'    : [] ,
                     'GridWidth' : 1 ,
                     'ShowCommandOutput' : 1
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
            <ShowCommandOutput>%(ShowCommandOutput)s</ShowCommandOutput>
            <CommandList>
                <!-- This is the sytax for command entries:
                <Command text="TEXT"><![CDATA[SHELLCOMMAND]]></Command>
                -->
            </CommandList>
        </Configuration>
    </SpecialConfigurations>
</CLLConfig>
""" % DefaultConfig

    @staticmethod
    def openConfigFile(fileName):
        """open the file, if it doesn't exist, create it, if it doesn't work 
        exit program with error message"""
        try:
            f = open(fileName,'r')
        except IOError:
            try:
                with open(fileName,'w') as f:
                    f.write(CConfigFileParser.ConfigFileDefaultContents)
                f.close()
                f = open(fileName,'r')
            except:
                CHelper.errorMessageAndExit("config File %s cannot be read or written!" % fileName)
        # here, f should be a valid file handle
        return f

    def getConfiguration(self):
        """
        Read and parse config File ~/.commandlinelauncher.xml with Commands-structure
        return read config or DefaultConfig on error
        """
        f = CConfigFileParser.openConfigFile(self.configFileName)
        config = {}
        try:
            tree = ET.parse(f)
            root = tree.getroot()
            # at the moment, no general configuration items defined
            # find first matching configuration within SpecialConfiguration tag
            matchingConfig = None
            for c in root.findall("./SpecialConfigurations/Configuration"):
                if(c.attrib['name'] == self.configName):
                    matchingConfig=c
                    break
            if(matchingConfig is not None):
                # matching config found, set options accordingly
                config['TitleString'] = matchingConfig.find('Title').text
                config['LabelString'] = matchingConfig.find('LabelText').text
                config['GridWidth'] = int(matchingConfig.find('GridWidth').text)
                config['ShowCommandOutput'] = int(matchingConfig.find('ShowCommandOutput').text)
                comLst = []
                for c in matchingConfig.findall("./CommandList/Command"):
                    comLst.append(CCommandDescription(c.attrib['text'], c.text))
                config['Commands'] = comLst
        except:
            config = {}
        # here f should be a valid file handle => close it
        f.close()
        
        # return read config or DefaultConfig on error
        if config:
            return config
        else:
            return CHelper.DefaultConfig

    def __init__(self, configFileName = None, configName = None):
        self.configFileName = configFileName
        self.configName = configName
       
        if(self.configFileName is None):
            self.configFileName = self.DefaultConfigFileName
        if(self.configName is None):
            # get config name from file name
            match = re.search('([^/]+).py$', sys.argv[0])
            self.configName = match.group(1)
            # take config name from argument if given 
            if(len(sys.argv) > 1):
                self.configName = sys.argv[1]

class CApplication(Tkinter.Frame):
    """A class that represents the applications window"""        

    # static variables
    UpdateInterval = 200

    def executeCommand(self, command):
        # dont allow multiple running threads
        if self.currentThread is not None:
            return

        #TODO: disable all buttons in GUI. This didnt work
            for button in self.commandButtons:
                button.config(state="disabled")
        
        self.currentThread = threading.Thread(target=os.system, args=(command,))
        #self.currentThread = threading.Thread(target=os.system, args=("ping -c 5 192.168.1.102",))
        self.currentThread.start()

    def updateGUI(self):
        # test if work thread is still working and update data and GUI if not
        if self.currentThread is not None and not self.currentThread.isAlive():
            self.currentThread = None
            
            #TODO: enable all buttons in GUI. This didnt work
            for button in self.commandButtons:
                button.config(state="normal")
            
        self.master.after(self.UpdateInterval, self.updateGUI)
        
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
           
    def __init__(self, master, config):
        Tkinter.Frame.__init__(self, master, padx=20, pady=20)
        self.master = master
        self.config = config
        self.currentThread = None
        self.buttonwidth = self.calculateButtonWidth()
        self.commandButtons = []
        """create the dialog and call the main loop"""
        gridwidth = self.config['GridWidth']
        self.pack()
        # add a title string to the top
        label = Tkinter.Label(self, text=self.config['LabelString'].decode("string_escape"))
        label.grid(row=0, columnspan=gridwidth, pady=(0, 20))
        # add the buttons for the system command
        nextrow = self.addButtons() + 1
        # maybe add text boxes and labels for cout and cerr of system commands 
        if(config['ShowCommandOutput'] > 0):
            label = Tkinter.Label(self, text='Standard Output')
            label.grid(row=nextrow, column=0, columnspan=gridwidth, pady=(20, 0), sticky=Tkinter.NW)
            nextrow += 1
            label = Tkinter.Label(self, text='Standard Error')
            label.grid(row=nextrow, column=0, columnspan=gridwidth, pady=(20, 0), sticky=Tkinter.NW)
            nextrow += 1
        # add a close-button and center 
        button = Tkinter.Button(self, text="Close", command=(lambda: CHelper.exitProgram(0)), width=self.buttonwidth)
        button.grid(row=nextrow, column=0, pady=(20, 0), columnspan=gridwidth)
        # update GUI periodically
        self.master.after(self.UpdateInterval, self.updateGUI)

if __name__ == '__main__':
    parser = CConfigFileParser()
    config = parser.getConfiguration()
    app = CApplication(Tkinter.Tk(), config)
    app.mainloop()
