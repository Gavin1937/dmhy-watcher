
# Simple Utility Class for working with discord-noticmd-bot
# Import this file to other python scripts to send message to discrod-noticmd-bot

import os, errno
from queue import Queue
from enum import IntEnum

__all__ = [
    'DiscordMsgStatus',
    'DiscordMsgUtil',
]


# https://stackoverflow.com/a/42239713
class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


class DiscordMsgStatus(IntEnum):
    FIFO_WRITE_FAIL           = 0
    FIFO_NOT_RESPONSE_ENXIO   = 1
    FIFO_WRITE_SUCCESS        = 2
    FIFO_BROKEN_EPIPE         = 3

class DiscordMsgUtil(Singleton):
    def __init__(self):
        self.__buffer:Queue = Queue()
        self.__fifo_path:str = None
        pass
    
    @property
    def buffer(self) -> list:
        return list(self.__buffer.queue)
    
    @property
    def fifo_path(self) -> str:
        return self.__fifo_path
    
    def update_fifo_path(self, fifo_path:str):
        if not os.path.exists(fifo_path):
            raise ValueError('Input fifo_path does not exists.')
        self.__fifo_path = fifo_path
        pass
    
    def clear_buffer(self):
        del self.__buffer
        self.__buffer = Queue()
    
    def send_message(self, message:str) -> DiscordMsgStatus:
        '''
        Parameter:
        ==========
            -   message: utf-8 string message write to fifo If message start with '@ ' (e.g. '@ new messages...')
                discord-noticmd-bot.py will mention the admin in this message. Be sure to include both '@' and ' ' characters
        '''
        
        if self.__fifo_path is None:
            raise ValueError('No valid fifo_path, please call self.update_fifo_path() first.')
        
        self.__buffer.put(message)
        try:
            fifo_file = os.open(self.__fifo_path, os.O_WRONLY | os.O_NONBLOCK)
        except OSError as exc:
            if exc.errno == errno.ENXIO:
                fifo_file = None
                return DiscordMsgStatus.FIFO_NOT_RESPONSE_ENXIO
            else:
                raise
        if fifo_file is not None:
            try:
                for _ in range(self.__buffer.qsize()):
                    os.write(fifo_file, self.__buffer.get())
            except OSError as exc:
                if exc.errno == errno.EPIPE:
                    return DiscordMsgStatus.FIFO_BROKEN_EPIPE
                else:
                    raise
            os.close(fifo_file)
            return DiscordMsgStatus.FIFO_WRITE_SUCCESS
        else:
            return DiscordMsgStatus.FIFO_WRITE_FAIL
