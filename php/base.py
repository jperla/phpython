import os
import sys
import logging
import traceback
from functools import partial

import weby
import tempy


def list_files_in_dir(dir, endswith=None):
    """Accepts directory and endswith strings.
        Yields generator of all files in subdirs.
    """
    for root, dirs, files in os.walk(dir):
        # jperla: +1 for '/'
        base = root[len(dir) + 1:]
        for f in files:
            if endswith is None or f.endswith(endswith):
                yield os.path.join(base, f)

def dictionary_router(dictionary, path):
    """Accepts dictionary and path string.
        '.../' directs to '.../index'.
        Returns string filename based on directory.
    """
    if path.endswith('/'):
        path += 'index' # default file in dir is index
    return dictionary.get(path.strip('/'))

def generate_router(directory):
    """Crawls all of the files in the directory.
        Accepts directory name string.
        Returns a routing function that accepts a string path and returns a string absoulte filename.
    """
    #TODO: jperla: crawl directories
    assert (os.path.exists(directory) and os.path.isdir(directory)), '%s is not a directory' % directory
    dictionary = dict((f[:-3], os.path.join(directory, f))
                        for f in list_files_in_dir(directory, '.py'))
    return partial(dictionary_router, dictionary)

def exec_php_file(filename, p, req, page):
    """Runs the filename in the context of these vars.
        Also sends the file the utility functions incude/require/etc.
    """
    #TODO: jperla: does this split stuff work robustly?
    in_dir,_ = os.path.split(filename)
    kwargs = {'req': req, 'page': page, 'in_dir': in_dir}

    #TODO: jperla: note that page is ignored...
    execfile(filename, {'req': req,
                        'p': p,
                        'page': page,
                        
                        # utility methods
                        'include': partial(include, p=p, **kwargs),
                        'include_inline': partial(include_inline, p=p, **kwargs),
                        'require_inline': partial(require_inline, p=p, **kwargs),

                        # methods that need just kwargs
                        'get_include_contents': partial(get_include_contents, **kwargs),
                        'load': partial(load, **kwargs),
                        'safe_load': partial(safe_load, **kwargs),
                        }
    )

@tempy.template()
def run_template(p, filename, req, page):
    """Accepts filename, request, and page object (to be returned).
        Runs the filename in the context of these vars.
        Content is accumulated in p, headers/status in page.
        Returns nothing.
    """
    try:
        exec_php_file(filename, p, req, page)
    except Exception:
        logging.error(get_traceback())
        page.status = '500 Server Error'
        #page.headers = {}
        #TODO: jperla: headers to what?
        #TODO: jperla: allow silencing of errors? clear p accumulator?

def include_inline(filename, p, req, page, in_dir):
    """Accepts accumulator, filename, req and page objects.
        Executes the filename on these inputs.
        Returns 'PHP'.
        Exceptions propagate up fatally.
    """
    full_path = os.path.join(in_dir, filename)
    exec_php_file(full_path, p, req, page)
    return 'PHP'

def get_include_contents(*args, **kwargs):
    """Same as include_inline, but doesn't accept accumululator, 
        so just returns string.
        Runs the file and accumulators html onto accumulator.
    """
    @tempy.template()
    def run(p):
        include_inline(*args, p=p, **kwargs)
    return run()

def get_traceback():
    """Returns formatted traceback."""
    exc_info = sys.exc_info()
    tb = u'\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))
    del exc_info
    return tb

def safe_decorator(method):
    """Accepts method.
        Returns wrapped function.
        Same as method() but catches errors and returns traceback.
    """
    def wrapper(*args, **kwargs):
        #TODO: jperla: refactor as decorator
        try:
            return method(*args, **kwargs)
        except Exception:
            #TODO: jperla: allow silencing of errors? clear p accumulator?
            silence = False
            if silence:
                return u''
            else:
                return get_traceback()
    return wrapper

require_inline = safe_decorator(include_inline)

# Interesting choice.  Make include return string, or insert directly into generator?
include = get_include_contents
load = get_include_contents
safe_load = safe_decorator(load)



def create_app(directory):
    """Creates a simple weby app that routes based on filenames.
        Accepts directory filename.
        Sets up sys.path on the directory.
        Returns the app.
    """
    router = generate_router(directory)
    app = weby.defaults.App()
    sys.path.append(directory)
    @app.default_subapp()
    @weby.urlable_page()
    def single_page(req, page):
        """Given the request and page, run the file and return the content.
        """
        #TODO: jperla: better 404 handling
        filename = router(req.path) or '404.py'

        import sys
        import datetime
        sys.stdout.write('%(ip)s - %(remote_user)s [%(time)s] "%(method)s %(query)s %(protocol)s" ' % {
                'ip': req.environ.get('HTTP_X_REAL_IP', '-'),
                'remote_user': req.environ.get('REMOTE_HOST', '-'),
                'time': datetime.datetime.now().strftime('%d/%b/%Y:%H:%M:%S %z'),
                'method': req.environ.get('REQUEST_METHOD', '-'),
                'protocol': req.environ.get('SERVER_PROTOCOL', '-'),
                'query': req.path_qs,
        })

        try:
            content = run_template(filename, req, page)
            page(content)
        except:
            sys.stdout.write('\n')
        else:
            sys.stdout.write('%s %s\n' % (page.status, len(content)))
    return app

