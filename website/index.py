import tempy
from tempy.helpers import html

title = 'PHPython: Python Hypertext Processor'

@tempy.template()
def main(p):
    with p(html.html()):
        with p(html.head()):
            p(html.title(title))
        with p(html.body()):
            p(html.h1(title))
            p(html.p(u"""
                Now, teams never have to choose between the ease of developing in PHP and the power and flexibility of Python.  Developers can get the best of both worlds with PHPython.
            """))
            p(html.h2('The simplest way to make a website in Python'))

            p(faq())
            p(html.a('Download the git repository', 
                    {'href': 'http://github.com/jperla/phpython'}))

@tempy.template()
def faq(p):
    p(faq_why())
    p(faq_how())

@tempy.template()
def faq_how(p):
    p(html.h3('How is it built?'))
    p(html.p(u"""
        PHPython doesn't invent anything.  It is a WSGI-compliant
        framework.  It leverages as much code as possible from the
        large Python ecosystem.
    """))
    p(html.p(u"""
        By default, PHPython uses Tornado server for fast web
        serving, Tempy for fast, native templating, PHP-like
        URL routing based on files and directories, and 
        WebOb for request objects.  
        Any component may be swapped out for your favorite.
        PHPython is very fast and flexible.
    """))
    p(html.p(u"""
        PHPython has live dynamic reload, full stack trace
        and debugging integration, and middleware support.
    """))
    p(html.p(u"""
        PHPython is explicit and has no magic. 
    """))

@tempy.template()
def faq_why(p):
    p(html.h3('Why PHPython?'))
    p(html.p(u"""
        Python is a terrific language.  It is readable, modular, and
        powerful and easy to use.
    """))
    p(html.p(u"""
        PHP has taught millions of people
        how to make websites.  It has a simple URL model and a low
        barrier to entry to get things done.
    """))
    p(html.p(u"""
        We can take the simplicity of PHP web development, and bring
        the best characteristics to Python.  This allows us to make a
        Python web framework (like Django) that is easy to write, simple
        to learn, and very powerful.
    """))
    

p(main())
