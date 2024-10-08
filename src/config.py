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

