import os
import argparse

from . import tinysite
from .localization import babel, locale_exists

def execute_manager(build_dir, static_files_dir, template_dir,
                    locale_dir, locale_domain,
                    babel_ini_file, template_vars):
    def cmd_makemessages(args):
        "create/update message file(s) for localization"
        
        potfile = os.path.join(locale_dir, '%s.pot' % locale_domain)

        localeargs = []
        cmd = 'update'
        
        if args.locale:
            localeargs.extend(['-l', args.locale])
            if not locale_exists(args.locale, locale_dir, locale_domain):
                cmd = 'init'

        babel(['extract', '-F', babel_ini_file, '-o', potfile,
               template_dir])
        
        babel([cmd, '-i', potfile, '-d', locale_dir, '-D', locale_domain] +
              localeargs)

    def cmd_compilemessages(args):
        "convert message files into binary format"

        babel(['compile', '--use-fuzzy', '-d', locale_dir, '-D',
               locale_domain])

    def cmd_build(args):
        "build static site"

        tinysite.export_site(
            build_dir=build_dir,
            static_files_dir=static_files_dir,
            template_dir=template_dir,
            locale_dir=locale_dir,
            locale_domain=locale_domain,
            template_vars=template_vars,
            )

    def cmd_runserver(args):
        "run development server"

        tinysite.run_server(
            port=args.port,
            static_files_dir=static_files_dir,
            template_dir=template_dir,
            locale_dir=locale_dir,
            locale_domain=locale_domain,
            template_vars=template_vars,
            )

    if not os.path.exists(locale_dir):
        os.mkdir(locale_dir)

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    build = subparsers.add_parser('build', help=cmd_build.__doc__)
    build.set_defaults(func=cmd_build)
    makemessages = subparsers.add_parser('makemessages', 
                                         help=cmd_makemessages.__doc__)
    makemessages.add_argument('-l', '--locale', help="locale")
    makemessages.set_defaults(func=cmd_makemessages)
    compilemessages = subparsers.add_parser('compilemessages',
                                            help=cmd_compilemessages.__doc__)
    compilemessages.set_defaults(func=cmd_compilemessages)
    runserver = subparsers.add_parser('runserver', help=cmd_runserver.__doc__)
    runserver.add_argument('--port', help='port to serve on',
                           type=int, default=8000)
    runserver.set_defaults(func=cmd_runserver)
    args = parser.parse_args()
    args.func(args)
