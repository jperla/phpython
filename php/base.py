import tempy
import weby

def generate_router(directory):
    """Crawls all of the files in the directory.
        Accepts directory name string.
        Returns a dictionary mapping urls to filenames.
    """
    #TODO: jperla: crawl directories
    import os
    assert (os.path.exists(directory) and os.path.isdir(directory)), '%s is not a directory' % directory
    files = os.listdir(directory)
    router = dict((f[:-3], os.path.join(directory, f)) for f in files if f.endswith('.py'))
    return router

def load(directory):
    """Creates a simple weby app that routes based on filenames.
        Accepts directory filename.
        Returns the app.
    """
    @tempy.template()
    def run_template(p, filename, req, page):
        """Accepts filename, request, and page object (to be returned).
            Runs the filename in the context of these vars.
            Content is accumulated in p, headers/status in page.
            Returns nothing.
        """
        execfile(filename, {'req': req, 'p': p, 'page': page})
    router = generate_router(directory)
    app = weby.defaults.App()
    @app.default_subapp()
    @weby.urlable_page()
    def single_page(req, page):
        """Given the request and page, run the file and return the content.
        """
        remaining = 'index' #TODO: jperla: get proper urlpath
        filename = router.get(remaining, '404.py')
        content = run_template(filename, req, page)
        page(content)
    return app
