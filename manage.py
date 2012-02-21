import sys
import os
import settings

ROOT = os.path.dirname(os.path.abspath(__file__))

def path(*a):
    return os.path.join(ROOT, *a)

sys.path.insert(0, path('vendor'))

from hackasaurus.management import execute_manager

if __name__ == '__main__':
    execute_manager(
        build_dir=path('dist'),
        static_files_dir=path('static'),
        template_dir=path('templates'),
        locale_dir=path('locale'),
        locale_domain='openbadges',
        babel_ini_file=path('babel.ini'),
        template_vars={'settings': settings}
        )
