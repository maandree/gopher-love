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

from argparser import *

from net import *
from config import *
from terminal import *



config_file = None
'''
:str?  The configuration file
'''

config_opts = None
'''
:list<str>  Options passed to the configuration script
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
        # Create string buffer with title
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


def main():
    '''
    This function is called directly after the rc-file has been loaded
    '''
    pass # TODO


## Read command line arguments
parser = ArgParser('An extensible gopher browser',
                   sys.argv[0] + ' [options] [-- configuration-options]',
                   None, None, True, ArgParser.standard_abbreviations())

parser.add_argumented(['-c', '--configurations'], 0, 'FILE', 'Select configuration file')
parser.add_argumentless(['-h', '-?', '--help'], 0, 'Print this help information')
parser.add_argumentless(['-C', '--copying', '--copyright'], 0, 'Print copyright information')
parser.add_argumentless(['-W', '--warranty'], 0, 'Print non-warranty information')
parser.add_argumentless(['-v', '--version'], 0, 'Print program name and version')

parser.parse()
parser.support_alternatives()

if parser.opts['--help'] is not None:
    parser.help()
    sys.exit(0)
elif parser.opts['--copyright'] is not None:
    print(copyright[1 : -1])
    sys.exit(0)
elif parser.opts['--warranty'] is not None:
    print(copyright.split('\n\n')[2])
    sys.exit(0)
elif parser.opts['--version'] is not None:
    print('%s %s' % (PROGRAM_NAME, PROGRAM_VERSION))
    sys.exit(0)

a = lambda opt : opt[0] if opt is not None else None
config_file = a(parser.opts['--configurations'])
config_opts = parser.files


## Load extension and configurations via gopher-loverc
def get_config_file():
    '''
    Find the default configuration file
    
    @return  :str?  The first found default configuration file, `None` if none found
    '''
    import pwd
    dirs = os.environ['XDG_CONFIG_DIRS'].split(':') if 'XDG_CONFIG_DIRS' in os.environ else []
    files = ['$XDG_CONFIG_DIRS/%rc'] * len(dirs)
    files = ['$XDG_CONFIG_HOME/%/%rc', '$HOME/.config/%/%rc', '$HOME/.%rc',
             '$~/.config/%/%rc', '$~/.%rc'] + files + ['/etc/%rc']
    home = pwd.getpwuid(os.getuid()).pw_dir.replace('$', '\0')
    for file in files:
        file = file.replace('%', PROGRAM_NAME)
        for arg in ('XDG_CONFIG_HOME', 'XDG_CONFIG_DIRS', 'HOME', '~'):
            if '$' + arg in file:
                if arg == 'XDG_CONFIG_DIRS':
                    dir, dirs = dirs[0].replace('$', '\0'), dirs[1:]
                    file = file.replace('$' + arg, dir)
                elif arg == '~':
                    file = file.replace('$' + arg, home)
                elif arg in os.environ:
                    file = file.replace('$' + arg, os.environ[arg].replace('$', '\0'))
                else:
                    file = None
                    break
        if file is not None:
            file = file.replace('\0', '$')
            if os.path.exists(file):
                return file
    return None
if config_file is None:
    config_file = get_config_file()
if config_file is not None:
    config_opts = [config_file] + config_opts
    code = None
    with open(config_file, 'rb') as script:
        code = script.read()
    code = code.decode('utf-8', 'error') + '\n'
    code = compile(code, config_file, 'exec')
    g, l = globals(), dict(locals())
    for key in l:
        g[key] = l[key]
    exec(code, g)


main()

