#!/usr/bin/env python 
import php

if __name__ == '__main__':
    port = 8054
    print 'Loading server on %s...' % port
    app = php.create_app('./website/')
    php.http.server.tornado.start(app, port=port, num_processes=1)

'''
app = php.apps.SettingsMiddleApp({
        'bpodb': bpodb,
        'filedb': filedb,
}, app)

cookie_secret = 'abenierns829839283irenst'
app = php.apps.InsecureCookieSessionMiddleApp(app, 'c', cookie_secret)
'''
