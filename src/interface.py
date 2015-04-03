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



hotkeys = {}
'''
:dict<str, ()→void>  Map from keyboard input to function to call for that input
'''


def clen(string, original_len = len):
    '''
    Colour-aware object length measurement function
    
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
    populate_hotkeys()
    
    try:
        initialise_terminal()
        hide_cursor()
        saved_stty = store_tty_settings()
        set_tty_settings(echo = False, isig = False, icanon = False, ixany = True, ixoff = False, ixon = False)
        set_up_winch_listener(lambda : None)
        
        cont = True
        while cont:
            print('\033[H\033[2J', end = '')
            (height, width) = get_terminal_size()
            draw_interface(1, 1, width, height)
            cont = interaction()
    finally:
        restore_tty_settings(saved_stty)
        show_cursor()
        uninitialise_terminal()


def draw_interface(x, y, width, height):
    '''
    Draw the interface
    
    @param  x:int                       The first column of the drawable area of the screen, one-based
    @param  y:int                       The first line of the drawable area of the screen, one-based
    @param  width:int                   The number of columns of the drawable area of the screen
    @param  height:int                  The number of lines of the drawable area of the screen
    @return  :(:int, :int, :int, :int)  Input parameter for the next interface drawing function
    '''
    size = (x, y, width, height)
    parts = (draw_interface_tab, draw_interface_status, draw_interface_page)
    for part in parts:
        size = part(*size)
    return size


def draw_interface_tabs(x, y, width, height):
    '''
    Draw the tab bar
    
    @param  x:int                       The first column of the drawable area of the screen, one-based
    @param  y:int                       The first line of the drawable area of the screen, one-based
    @param  width:int                   The number of columns of the drawable area of the screen
    @param  height:int                  The number of lines of the drawable area of the screen
    @return  :(:int, :int, :int, :int)  Input parameter for the next interface drawing function
    '''
    bar = 'Welcome'
    bar = '\033[01;34;47m%s\033[00;07m' % bar
    bar += ' ' * (width - clen(bar))
    print('\033[%i;%iH\033[07m%s\033[m' % (y, x, bar), end = '', flush = True)
    y += 1
    height -= 1
    return (x, y, width, height)


def draw_interface_status(x, y, width, height):
    '''
    Draw the status bar
    
    @param  x:int                       The first column of the drawable area of the screen, one-based
    @param  y:int                       The first line of the drawable area of the screen, one-based
    @param  width:int                   The number of columns of the drawable area of the screen
    @param  height:int                  The number of lines of the drawable area of the screen
    @return  :(:int, :int, :int, :int)  Input parameter for the next interface drawing function
    '''
    print('\033[%i;%iH\033[07m%s\033[m' % (y + height, x, ' ' * width), end = '', flush = True)
    height -= 1
    return (x, y, width, height)


def draw_interface_page(x, y, width, height):
    '''
    Draw the page
    
    @param  x:int                       The first column of the drawable area of the screen, one-based
    @param  y:int                       The first line of the drawable area of the screen, one-based
    @param  width:int                   The number of columns of the drawable area of the screen
    @param  height:int                  The number of lines of the drawable area of the screen
    @return  :(:int, :int, :int, :int)  Input parameter for the next interface drawing function
    '''
    print('\033[%i;%iH%s' % (y, x, 'Welcome to gopher-love'))
    return (x, y, 0, 0)


_interation_redraw = False
_interation_quit = False
def interaction():
    '''
    Interaction loop
    
    @return  :bool  `True` for redrawing the interface, `False` for exiting
    '''
    global _interation_redraw, _interation_quit
    _interation_redraw = False
    _interation_quit = False
    while True:
        input = read_terminal_input()
        if input is None:
            _interation_redraw = True
        elif input in hotkeys:
            hotkeys[input]()
        else:
            keyboard_pressed(input);
        if _interation_quit:
            return False
        if _interation_redraw:
            return True


def force_redraw():
    '''
    Tell the interface that it needs to be redrawn
    '''
    global _interation_redraw
    _interation_redraw = True


def exit_program():
    '''
    Tell the program to exit
    '''
    global _interation_quit
    _interation_quit = True


def populate_hotkeys():
    '''
    Populate the hotkey map
    '''
    hotkeys[ctrl('L')] = force_redraw
    hotkeys[ctrl('Q')] = exit_program


def keyboard_pressed(input):
    '''
    This function is called when a keyboard input not mapped as a hotkey
    
    @param  input:str  The keyboard input
    '''
    pass

