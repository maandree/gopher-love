#!/usr/bin/env python3
copyright='''
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
import os, sys

from net import *


PROGRAM_NAME = 'gopher-love'
'''
:str  The name of the program
'''

PROGRAM_VERSION = 'devel'
'''
:str  The version of the program
'''


default_protocol = 'gopher'
'''
:str  The protocol to use when no protocol has been specified
'''

default_port = {'gopher' : 70}
'''
:dict<str, int>  The port to use for each protocol when no port has been specified
'''

config_file = None
'''
:str?  The configuration file
'''


## Set process title
def setproctitle(title):
    '''
    Set process title
    
    @param  title:str  The title of the process
    '''
    import ctypes
    try:
        # Remove path, keep only the file,
        # otherwise we get really bad effects, namely
        # the name title is truncates by the number
        # of slashes in the title. At least that is
        # the observed behaviour when using procps-ng.
        title = title.split('/')[-1]
        # Create strng buffer with title
        title = title.encode(sys.getdefaultencoding(), 'replace')
        title = ctypes.create_string_buffer(title)
        if 'linux' in sys.platform:
            # Set process title on Linux
            libc = ctypes.cdll.LoadLibrary('libc.so.6')
            libc.prctl(15, ctypes.byref(title), 0, 0, 0)
        elif 'bsd' in sys.platform:
            # Set process title on at least FreeBSD
            libc = ctypes.cdll.LoadLibrary('libc.so.7')
            libc.setproctitle(ctypes.create_string_buffer(b'-%s'), title)
    except:
        pass
setproctitle(sys.argv[0])


## Load extension and configurations via gopher-loverc
def get_config_file():
    '''
    Find the default configuration file
    
    @return  :str?  The first found default configuration file, `None` if none found
    '''
    import pwd
    # TODO add support for $XDG_CONFIG_DIRS
    files = ('$XDG_CONFIG_HOME/%/%rc', '$HOME/.config/%/%rc', '$HOME/.%rc',
             '$~/.config/%/%rc', '$~/.%rc', '/etc/%rc')
    for file in files:
        file = file.replace('%', PROGRAM_NAME)
        for arg in ('XDG_CONFIG_HOME', 'HOME'):
            if '$' + arg in file:
                if arg in os.environ:
                    file = file.replace('$' + arg, os.environ[arg].replace('$', '\0'))
                else:
                    file = None
                    break
        if file is not None:
            if file.startswith('$~'):
                file = pwd.getpwuid(os.getuid()).pw_dir + file[2:]
            file = file.replace('\0', '$')
            if os.path.exists(file):
                return file
    return None
if config_file is None:
    config_file = get_config_file()
if config_file is not None:
    code = None
    with open(config_file, 'rb') as script:
        code = script.read()
    code = code.decode('utf-8', 'error') + '\n'
    code = compile(code, config_file, 'exec')
    g, l = globals(), dict(locals())
    for key in l:
        g[key] = l[key]
    exec(code, g)

