import Tkinter
import tkMessageBox

class CMyToolbox:
    """ class for general tools """
    @staticmethod        
    def exitProgram(status):
        """exit this Python script"""    
        Tkinter.sys.exit(status)

    @staticmethod
    def errorMessageAndExit(message):
        """Show an error message box and exit"""
        tkMessageBox.showerror("Command Line Launcher", message)    
        CMyToolbox.exitProgram(1)

