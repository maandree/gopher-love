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


def connect(host, port, protocol = 'tcp'):
    '''
    Connect to a server using `netcat`
    
    @param   host:str      The host to connect to
    @param   port:int      The port to connect to
    @param   protocol:str  The protocol to use
    @return  :Popen        Control object for the created instance `netcat`
    '''
    from subprocess import Popen, PIPE
    Popen(['nc', {'tcp' : '-t', 'udp' : '-p'}[protocol.lower()], hostname, str(port)],
          stdin = PIPE, stdout = PIPE, stderr = PIPE)


def punycode(address): # TODO
    return address


def parse_url(): # TODO
    pass


def construct_url(scheme, user, password, domain, port, path, query_string, fragment_id, *, **extras):
    '''
    Construct an URL
    
    This function supports generic syntax and gopher
    
    @param   scheme:str?        The protocol, `None` to omit
    @param   user:str?          The username, `None` to omit
    @param   password:str?      The password, `None` to omit
    @param   domain:str?        The hostname, `None` to omit
    @param   port:int|str?      The port, `None` to omit
    @param   path:str?          The pathname, `None` to omit
    @param   query_string:str?  The query, `None` to omit
    @param   fragment_id:str?   The anchor, `None` to omit
    @param   extras:**          Extras scheme specific parameters,
                                'item_type' is available for gopher
    @return  :str               The URL
    '''
    domain = punycode(domain)
    port = str(port)
    item_type = extras['item_type'] if (scheme == 'gopher') and ('item_type' in extras) else None
    reserved = '%!*\'();:@&=+$,/?#[]' # % must be first
    for c in range(0, ord(' ')):
        reserved += chr(c)
    for c in reserved:
        cc = '%02x' % c.encode('utf-8')[0]
        if scheme       is not None:                    scheme       = scheme      .replace(c, cc)
        if user         is not None:                    user         = user        .replace(c, cc)
        if password     is not None:                    password     = password    .replace(c, cc)
        if domain       is not None and c not in ':':   domain       = domain      .replace(c, cc)
        if port         is not None:                    port         = port        .replace(c, cc)
        if path         is not None and c not in '/':   path         = path        .replace(c, cc)
        if query_string is not None and c not in '&=':  query_string = query_string.replace(c, cc)
        if fragment_id  is not None:                    fragment_id  = fragment_id .replace(c, cc)
        if item_type    is not None:                    item_type    = item_type   .replace(c, cc)
    string = ''
    while '//' in path:
        path = path.replace('//', '/')
    if scheme       is not None:  string += scheme + '://'
    if user         is not None:  string += user
    if password     is not None:  string += ':' + password
    if user is not None or password is not None:
        string += '@'
    if domain       is not None:  string += '[%s]' % domain if ':' in domain else domain
    if port         is not None:  string += ':%i' % port
    if path         is not None:  string += '/' + ('' if item_type is None else item_type) + path.lstrip('/')
    if query_string is not None:  string += '?' + query_string
    if fragment_id  is not None:  string += '#' + fragment_id
    return ''.join(chr(c) if c < 128 else ('%02x' % c) for c in string.encode('utf-8'))

