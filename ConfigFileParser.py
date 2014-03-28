import os
import sys
import re
import xml.etree.ElementTree as ET
# local imports
from MyToolbox import CMyToolbox

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
                CMyToolbox.errorMessageAndExit("config File %s cannot be read or written!" % fileName)
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
            return self.DefaultConfig

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

