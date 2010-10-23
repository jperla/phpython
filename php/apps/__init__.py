import weby
from weby.apps import *

import urllib
import simplejson
class InsecureCookieSessionMiddleApp(weby.apps.MiddleApp):
    def __init__(self, f, cookie_name, cookie_secret):
        self._f = f
        self.cookie_name = cookie_name
        self.cookie_secret = cookie_secret
    def __call__(self, req):
        cookie = req.cookies.get(self.cookie_name)
        if cookie is not None:
            # #TODO: jperla: do other things here, securely
            cookie_data = simplejson.loads(urllib.unquote(cookie))
        else:
            cookie_data = {}
        req.session = cookie_data

        response = self._f(req)

        status, headers = response.next()
        def create_cookie_header(name, data, path='/', expires=None, domain=None):
            if domain is not None or expires is not None:
                # #TODO: jperla: implement these
                raise NotImplementedError
            encoded_data = urllib.quote(simplejson.dumps(data))
            data_string = '%s=%s' % (name, encoded_data)
            cookie_fields = [data_string, 'Path=%s' % path,]
            cookie_value = ';'.join(cookie_fields)
            return ('Set-Cookie', cookie_value)
        #TODO: jperla: inefficient, always resetting whole cookie
        new_headers = headers + [ create_cookie_header(self.cookie_name, req.session),
                                    ('Cache-Control', 'no-cache, no-store'), 
                                    ('Pragma', 'no-cache'), ]
        yield status, new_headers
        for r in response:
            yield r
