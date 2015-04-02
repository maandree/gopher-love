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


def punycode(address):
    '''
    Convert an IDN address to traditional limited ASCII format using punycode
    
    @param   address:str  The IDN address in UCS
    @return  :str         The IDN address in punycode
    '''
    import encodings.punycode
    return encodings.punycode.punycode_encode(address).decode('utf-8', 'strict').rstrip('-')


def parse_url(url, fallback_scheme):
    '''
    Parse an URL string
    
    This function supports generic syntax and gopher
    
    @param   url:str              The URL string
    @param   fallback_scheme:str  The scheme to assume the URL uses if
                                  the URL string does not contain any
    @return  :dict<str, ¿V?>      Parameters from `construct_url`, `**extras` in
                                  `construct_url` is unioned with the other parameters.
                                  Omitted parameters are not included. String will not
                                  be unescaped, they will be returned in %-escaped form
    '''
    rc = {}
    scheme = fallback_scheme
    if '://' in url:
        parts = url.split('://')
        scheme, url = parts[0], '://'.join(parts[1:])
        rc['scheme'] = scheme
    if '?' in url:
        parts = url.split('?')
        url, query = parts[0], '?'.join(parts[1:])
        parts = query.split('#')
        query, url = parts[0], url + '#'.join(parts[1:])
        rc['query_string'] = query_string
    if '#' in url:
        parts = url.split('#')
        url, fragment = parts[0], '#'.join(parts[1:])
        rc['fragment_id'] = fragment
    if '/' in url:
        parts = url.split('/')
        url, path = parts[0], '/'.join(parts[1:])
        if (scheme == 'gopher') and (not path == ''):
            item_type, path = path[0], path[1:]
            rc['item_type'] = item_type
        rc['path'] = '/' + path
    if '@' in url:
        parts = url.split('@')
        login, url = parts[0], '@'.join(parts[1:])
        parts = login.split(':')
        user, password = parts[0], ':'.join(parts[1:])
        if not user == '':
            rc['user'] = user
        if not password == '':
            rc['password'] = password
    if '[' in url:
        url = url.replace('[', '')
        parts = url.split(']')
        domain, url = parts[0], ']'.join(parts[1:])
    elif ':' in url:
        parts = url.split(':')
        domain, url = parts[0], ':'.join(parts[1:])
    else:
        domain, url = url, ''
    rc['domain'] = domain
    if not url == '':
        try:
            rc['port'] = int(port)
        except:
            rc['port'] = port
    return rc


def construct_url(scheme, user, password, domain, port, path, query_string, fragment_id, **extras):
    '''
    Construct an URL string
    
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
    url = ''
    while '//' in path:
        path = path.replace('//', '/')
    if scheme       is not None:  url += scheme + '://'
    if user         is not None:  url += user
    if password     is not None:  url += ':' + password
    if user is not None or password is not None:
        url += '@'
    if domain       is not None:  url += '[%s]' % domain if ':' in domain else domain
    if port         is not None:  url += ':%i' % port
    if path         is not None:  url += '/' + ('' if item_type is None else item_type) + path.lstrip('/')
    if query_string is not None:  url += '?' + query_string
    if fragment_id  is not None:  url += '#' + fragment_id
    return ''.join(chr(c) if c < 128 else ('%02x' % c) for c in url.encode('utf-8'))


def url_unescape(text):
    '''
    Unescape a %-escaped string in an URL
    
    @param   text:str  The %-escaped string
    @return  :str      The string, unescaped
    '''
    buf, esc, a, b = [], False, None, None
    for c in text:
        if esc:
            if a is None:
                a = c
            else:
                esc = False
                b = c
                buf.append(int(a + b, 16))
        elif c == '%':
            esc, a, b = True, None, None
        else:
            buf.append(ord(c))
    return bytes(buf).decode('utf-8', 'strict')

