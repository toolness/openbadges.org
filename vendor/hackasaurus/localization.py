import os
import sys

from babel import Locale, UnknownLocaleError
from babel.messages.frontend import CommandLineInterface

class SimpleLocale(object):
    def __init__(self, name):
        self.__locale = Locale.parse(name)
        self.display_name = self.__locale.display_name
    
    def __str__(self):
        return hyphenate(str(self.__locale))

def hyphenate(name):
    return name.replace('_', '-')

def unhyphenate(name):
    return name.replace('-', '_')

def to_gettext_locale(name):
    try:
        return str(Locale.parse(name, sep='-'))
    except (ValueError, UnknownLocaleError):
        return None

def find_locales(dirname, domain, default):
    locales = {}
    for name in [name for name in os.listdir(dirname)
                 if locale_exists(name, dirname, domain)]:
        locales[hyphenate(name)] = SimpleLocale(name)
    locales[hyphenate(default)] = SimpleLocale(default)
    return locales
    
def locale_exists(locale, dirname, domain):
    pofile = os.path.join(dirname, locale, 'LC_MESSAGES',
                          '%s.po' % domain)
    return os.path.exists(pofile)

def babel(args):
    cmdline = CommandLineInterface()
    cmdline.usage = 'pybabel %s %s'
    print "calling pybabel %s" % (" ".join(args))
    cmdline.run([sys.argv[0]] + args)

