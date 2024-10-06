# -*- python -*-
'''
gopher-love – an extensible gopher browser
Copyright © 2015  Mattias Andrée (m@maandree.se)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, sys, termios



def hide_cursor():
    '''
    Hide the cursor in the terminal
    '''
    sys.stdout.buffer.write('\033[?25l'.encode('utf-8'))
    sys.stdout.buffer.flush()


def show_cursor():
    '''
    Show the cursor in the terminal
    '''
    sys.stdout.buffer.write('\033[?25h'.encode('utf-8'))
    sys.stdout.buffer.flush()


def initialise_terminal():
    '''
    Initialise the terminal
    '''
    sys.stdout.buffer.write('\033[?1049h'.encode('utf-8'))
    sys.stdout.buffer.flush()


def uninitialise_terminal():
    '''
    Uninitialise the terminal
    '''
    sys.stdout.buffer.write('\033[?1049l'.encode('utf-8'))
    sys.stdout.buffer.flush()


def store_tty_settings():
    '''
    Get current TTY settings
    
    @return  :¿?  Settings in a format readable by `restore_tty_settings`
    '''
    return termios.tcgetattr(sys.stdout.fileno())


def restore_tty_settings(settings):
    '''
    Set TTY settings
    
    @param  settings:¿?  Settings in the format used in the return by `store_tty_settings`
    '''
    termios.tcsetattr(sys.stdout.fileno(), termios.TCSAFLUSH, settings)


def set_tty_settings(echo = None, isig = None, icanon = None, ixany = None, ixoff = None, ixon = None):
    '''
    Change terminal settings
    
    @param  echo:bool?    Should echoing be enabled, `None` to keep unchanged
    @param  isig:bool?    Should input signals be enabled, `None` to keep unchanged
    @param  icanon:bool?  Should input buffering be enabled, `None` to keep unchanged
    @param  ixany:bool?   Should any character restart output, `None` to keep unchanged
    @param  ixoff:bool?   Should sending of start/stop character be enabled, `None` to keep unchanged
    @param  ixon:bool?    Should XON/XOFF flow control be enabled, `None` to keep unchanged
    '''
    stty = termios.tcgetattr(sys.stdout.fileno())
    
    flags = termios.ECHO, termios.ISIG, termios.ICANON
    settings = echo, isig, icanon
    turn_off, turn_on = 0, 0
    for flag, setting in zip(flags, settings):
        if setting is not None:
            turn_off |= flag if setting == False else 0
            turn_on  |= flag if setting == True  else 0
    stty[3] &= ~turn_off
    stty[3] |= turn_on
    
    flags = termios.IXANY, termios.IXOFF, termios.IXON
    settings = ixany, ixoff, ixon
    turn_off, turn_on = 0, 0
    for flag, setting in zip(flags, settings):
        if setting is not None:
            turn_off |= flag if setting == False else 0
            turn_on  |= flag if setting == True  else 0
    stty[0] &= ~turn_off
    stty[0] |= turn_on
    
    termios.tcsetattr(sys.stdout.fileno(), termios.TCSAFLUSH, stty)


def set_up_winch_listener(callback):
    '''
    Select function to be called when the terminal change size
    
    @param  callback:()→void  The function to call when the terminal change size
    '''
    import signal
    def proxy_callback(sig, _stack):
        signal.signal(sig, proxy_callback)
        callback()
    signal.signal(signal.SIGWINCH, proxy_callback)


def get_terminal_size():
    '''
    Get the size of the terminal
    
    @param  :(lines:int, columns:int)  The height and width of the terminal
    '''
    import struct, fcntl
    return struct.unpack('hh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234'))


_terminal_input_buffer = []
_terminal_input_fileno = sys.stdin.fileno()
def read_terminal_input():
    '''
    Read a single input from the terminal
    
    @return  :str?  The input unit, `None` if interrupted
    '''
    rc, buffer, utf8n, utf8c, esc = '', [], 0, 0, False
    try:
        while True:
            if len(_terminal_input_buffer) == 0:
                c = os.read(_terminal_input_fileno, 1)[0] # interruptable
            else:
                c = _terminal_input_buffer[0]
                _terminal_input_buffer[:] = _terminal_input_buffer[1:]
            buffer.append(c)
            if utf8n > 0:
                utf8n -= 1
                utf8c = (utf8c << 6) | (c & 0x3F)
                if utf8n == 0:
                    c = chr(utf8c)
                else:
                    continue
            elif (c & 0xC0) == 0xC0:
                utf8n = 0
                while (c & 0x80) == 0x80:
                    utf8n += 1
                    c <<= 1
                utf8c = (c & 0xFF) >> utf8n
                utf8n -= 1
                continue
            else:
                c = chr(c)
            if esc > 0:
                rc += c
                if esc == 0:
                    if c in '[O':
                        esc = 1
                    else:
                        break
                elif c not in '1234567890;':
                    esc = 0
                    break
            elif c == '\033':
                rc += c
                esc = 0
            else:
                rc += c
                break
    except InterruptedError:
        rc = None
        _terminal_input_buffer[:] = buffer
    return rc


def ctrl(key):
    '''
    Get the character sequence for a key combined with the control modifier
    
    @param   key:str  The key
    @return  :str     The key with the control modifier
    '''
    return chr(ord(key) - ord('@'))


def meta(key):
    '''
    Get the character sequence for a key combined with the meta modifier
    
    @param   key:str  The key
    @return  :str     The key with the meta modifier
    '''
    return '\033' + key

