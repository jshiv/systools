import os
import sys
import logging
import traceback

class StreamOut(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    level = logging.INFO
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''
 
    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip()+'\n')
            
    def flush(self):
        self.logger.flush()

class Stream(logging.StreamHandler):
    levels = {1: (logging.INFO, 'INFO'), 2: (logging.ERROR, 'ERROR')}

    def write(self, message):
        log_event = {'msg': message, 'levelno': self.level,
                    'levelname': self.levelname, 'name': self._name}
        record = self.makeRecord(**log_event)
        self.emit(record)
        self.flush()
        
    def makeRecord(self, **kwargs):
        record = logging.makeLogRecord(kwargs)
        return record
    
    
class StreamToTerminal(Stream):
    streamers = {1: sys.__stdout__, 2: sys.__stderr__}
    
    
    def __init__(self, file_desc=1):
        
        stream = self.streamers[file_desc]
        self._name = self.__class__
        super(self.__class__, self).__init__(stream)
        self.level, self.levelname = self.levels[file_desc]
        
class StreamToNotebook(Stream):
    streamers = {1: sys.stdout, 2: sys.stderr}
    def __init__(self, file_desc=1):
        
        self._name = self.__class__
        stream = self.streamers[file_desc]
        self.level, self.levelname = self.levels[file_desc]
        super(self.__class__, self).__init__(stream)
        
class StreamToFile(Stream):
    
    def __init__(self, file_desc=1):
        
        self.level, self.levelname = self.levels[file_desc]
        self._name = self.__class__
        filename = 'out.log'
        
        super(self.__class__, self).__init__(open(filename, 'a'))
        self.__dict__['close'] = logging.FileHandler.close
        self.set_format()
        
    def set_format(self):
        fmt = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
        formatter = logging.Formatter(fmt)
        self.setFormatter(formatter)        
        
class ExceptionToStreamOut(object):
    level = logging.ERROR
    
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''
        
    def __call__(self, exctype, value, traceback):
        self.logger.log(self.log_level, exctype)
        self.logger.log(self.log_level, value)
        for line in traceback.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
            
    def write(self):
        pass
    
    def flush(self):
        pass
            
        
class IExceptionToStreamOut(ExceptionToStreamOut):
        
    def __call__(self):
        traceback_lines = traceback.format_exception(*sys.exc_info())
        del traceback_lines[1]
        message = ''.join(traceback_lines)
        self.write(message)

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
        
        
class ExceptionToTerminal(StreamToTerminal):
    def __init__(self, fd=2):
        self.fd = fd
        
    def __call__(self,  exctype, value, traceback):
        self.write(exctype)
        self.write(value)
        for line in traceback.rstrip().splitlines():
            self.write(line.rstrip())
        self.flush()
        
class IExceptionToTerminal(ExceptionToTerminal):
    
    def __call__(self):
        traceback_lines = traceback.format_exception(*sys.exc_info())
        del traceback_lines[1]
        message = ''.join(traceback_lines)
        self.write(message)
        
    
class ExceptionToNotebook(object):
    from IPython.core.interactiveshell import InteractiveShell
    
    def __init__(self):
        pass
    
    def __call__(self):
        return self.InteractiveShell.showtraceback
    
    def write(self):
        pass

    def flush(self):
        pass