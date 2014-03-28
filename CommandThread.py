import threading
import subprocess

class CCommandThread(threading.Thread):
    """ class to handle the thread for the command line and the output buffer """   
    def __init__(self):
        """ the constructor creates the internal variables and the Lock """
        self.mutex = threading.Lock()
        self.command = ""
        self.out_lines = []
        threading.Thread.__init__(self)
    
    def dumpOutputLines(self):
        """ dump all lines in output buffer, clear buffer, when dumped. 
        Output buffer contains stderr and stdout of the command """
        with self.mutex:
            out = list(self.out_lines)
            self.out_lines = [] 
        return out

    def _appendOutputLine(self, line):
        """ append a line to the output buffer """
        with self.mutex:
            self.out_lines.append(line)
    
    def setCommand(self, command):
        """ set the command line, that will be called, when thread starts. """
        if not self.is_alive():
            with self.mutex:
                # connect stderr to stdout
                self.command = "( " + command + ") 2>&1"
            return True
        else:
            return False
      
    def _getCommand(self):
        """ returns the command line. """
        with self.mutex:
            command = self.command
        return command
    
    def isRunning(self):
        """ returns True, if thread is active or buffer is not empty """
        return (self.is_alive() or len(self.out_lines) != 0)            
    
    def run(self):
        """ start thread and read all output. """
        print "Start ThreadSlave"       
        proc=subprocess.Popen(self._getCommand(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # read lines until end of file
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            self._appendOutputLine(line)
        print "End ThreadSlave"
