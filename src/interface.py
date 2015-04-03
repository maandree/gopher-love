# -*- python -*-
'''
gopher-love – an extensible gopher browser
Copyright © 2015  Mattias Andrée (maandree@member.fsf.org)

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

from terminal import *



def clen(string, original_len = len):
    '''
    Colour-aware object length measurement function
    
    It is suggested to redefine `len` with this
    function in the following way.
    
        len_ = len
        len = lambda string : colour_aware_len(string, len_)
    
    @param   string:object              The object to measure
    @param   original_len:(object)→int  The original implementation of `len`
    @return  :int                       The length of `string`
    '''
    if not isinstance(string, str):
        return original_len(string)
    rc, esc = 0, False
    for c in string:
        if esc:
            if c == 'm':
                esc = False
        elif c == '\033':
            esc = True
        else:
            rc += 1
    return rc


def start_interface():
    '''
    Start the user interface
    '''
    saved_stty = None
    try:
        initialise_terminal()
        hide_cursor()
        saved_stty = store_tty_settings()
        set_tty_settings(echo = False, isig = False, icanon = False)
        set_up_winch_listener(lambda : None)
        
        while True:
            print('\033[H\033[2J', end = '')
            (height, width) = get_terminal_size()
            draw_interface(1, 1, width, height)
    finally:
        restore_tty_settings(saved_stty)
        show_cursor()
        uninitialise_terminal()


def draw_interface(x, y, width, height):
    bar = 'Welcome'
    bar = '\033[01;34;47m%s\033[00;07m' % bar
    bar += ' ' * (width - clen(bar))
    print('\033[%i;%iH\033[07m%s\033[m' % (y, x, bar), end = '', flush = True)
    y += 1
    height -= 1
    print('\033[%i;%iH\033[07m%s\033[m' % (y + height, x, ' ' * width), end = '', flush = True)
    height -= 1
    while True:
        input = read_terminal_input()
        if (input is None) or (input == ctrl('L')):
            return

