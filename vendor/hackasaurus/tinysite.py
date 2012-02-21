import os
import re
import mimetypes
import traceback
import shutil
import gettext
import jinja2
from distutils.dir_util import mkpath
from wsgiref.simple_server import make_server
from wsgiref.util import FileWrapper, shift_path_info

from .localization import find_locales, to_gettext_locale, hyphenate

mimetypes.add_type('application/x-font-woff', '.woff')

# Don't require localization files to exist for this locale.
NULL_LOCALE = 'en_US'

def simple_response(start, contents, code='200 OK', mimetype='text/plain'):
    start(code, [('Content-Type', mimetype),
                 ('Content-Length', str(len(contents)))])
    return [contents]

def handle_request(env, start, handlers):
    try:
        for handler in handlers:
            response = handler(env, start)
            if response is not None:
                return response
        return simple_response(start, "Not Found: %s" % env['PATH_INFO'],
                               code='404 Not Found')
    except Exception:
        msg = "500 INTERNAL SERVER ERROR\n\n%s" % traceback.format_exc()
        return simple_response(start, msg, code='500 Internal Server Error')

class BasicFileServer(object):
    def __init__(self, static_files_dir):
        self.ext_handlers = {}
        self.default_filenames = ['index.html']
        self.static_files_dir = static_files_dir

    def try_loading(self, filename, env, start):
        static_files_dir = self.static_files_dir
        fileparts = filename[1:].split('/')
        fullpath = os.path.join(static_files_dir, *fileparts)
        fullpath = os.path.normpath(fullpath)
        if (fullpath.startswith(static_files_dir) and
            not fullpath.startswith('.')):
            if os.path.isfile(fullpath):
                ext = os.path.splitext(fullpath)[1]
                handler = self.ext_handlers.get(ext)
                if handler:
                    mimetype, contents = handler(env, static_files_dir, fullpath)
                    return simple_response(start, contents, mimetype=mimetype)
                (mimetype, encoding) = mimetypes.guess_type(fullpath)
                if mimetype:
                    filesize = os.stat(fullpath).st_size
                    start('200 OK', [('Content-Type', mimetype),
                                     ('Content-Length', str(filesize))])
                    return FileWrapper(open(fullpath, 'rb'))
            elif os.path.isdir(fullpath) and not filename.endswith('/'):
                start('302 Found', [('Location', env['SCRIPT_NAME'] +
                                                 filename + '/')])
                return []
        return None

    def handle_request(self, env, start):
        filename = env['PATH_INFO']

        if filename.endswith('/'):
            for index in self.default_filenames:
                result = self.try_loading(filename + index, env, start)
                if result is not None:
                    return result
        return self.try_loading(filename, env, start)

class LocaleRedirectorServer(object):
    def __init__(self, template_dir,
                 redirect_template='locale-redirector.html'):
        self.redirect_template = redirect_template
        self.file_server = BasicFileServer(template_dir)
        self.file_server.ext_handlers.update({
            '.html': self.handle_file_as_jinja2_template
        })

    def handle_file_as_jinja2_template(self, wsgi_env, root_dir, fullpath):
        loader = jinja2.FileSystemLoader(root_dir, encoding='utf-8')
        env = jinja2.Environment(loader=loader)
        env.globals.update(dict(PATH_INFO=wsgi_env['PATH_INFO']))
        template = env.get_template(self.redirect_template)
        return ('text/html', template.render().encode('utf-8'))

    def handle_request(self, env, start):
        return self.file_server.handle_request(env, start)

class LocalizedTemplateServer(object):
    def __init__(self, template_dir, locale_dir, locale_domain,
                 template_vars):
        self.locale_dir = locale_dir
        self.locale_domain = locale_domain
        self.file_server = BasicFileServer(template_dir)
        self.file_server.ext_handlers.update({
            '.html': self.handle_file_as_jinja2_template
        })
        self.template_vars = template_vars

    def maybe_apply_translation(self, env, locale):
        env['locale'] = hyphenate(locale)
        if gettext.find(self.locale_domain, self.locale_dir, [locale]):
            env['translation'] = gettext.translation(self.locale_domain,
                                                     self.locale_dir,
                                                     [locale])

    def handle_request(self, env, start):
        parts = env['PATH_INFO'].split('/')[1:]
        locale = None
        if len(parts):
            locale = to_gettext_locale(parts[0])
        if locale:
            env = dict(env)
            shift_path_info(env)
            self.maybe_apply_translation(env, locale)
            if 'translation' in env or locale == NULL_LOCALE:
                return self.file_server.handle_request(env, start)

    def handle_file_as_jinja2_template(self, wsgi_env, root_dir, fullpath):
        loader = jinja2.FileSystemLoader(root_dir, encoding='utf-8')
        env = jinja2.Environment(loader=loader, 
                                 extensions=['jinja2.ext.i18n'])
        locales = find_locales(self.locale_dir, self.locale_domain,
                               NULL_LOCALE)
        env.globals.update(dict(
            LOCALE_ROOT="/%s/" % wsgi_env['locale'],
            locales=sorted(locales.values()),
            current_locale=locales[wsgi_env['locale']]
        ))
        env.globals.update(self.template_vars)
        if 'translation' in wsgi_env:
            env.install_gettext_translations(wsgi_env['translation'])
        else:
            env.install_null_translations(newstyle=True)
        template = env.get_template(fullpath[len(root_dir):])
        return ('text/html', template.render().encode('utf-8'))

def run_server(port, static_files_dir, template_dir,
               locale_dir, locale_domain, template_vars):
    template_server = LocalizedTemplateServer(template_dir, locale_dir,
                                              locale_domain, template_vars)
    locale_redirector = LocaleRedirectorServer(template_dir)
    file_server = BasicFileServer(static_files_dir)
    handlers = [template_server.handle_request,
                file_server.handle_request,
                locale_redirector.handle_request]

    def application(env, start):
        return handle_request(env, start, handlers=handlers)

    httpd = make_server('', port, application)

    url = "http://127.0.0.1:%s/" % port
    print "development server started at %s" % url
    print "press CTRL-C to stop it"

    httpd.serve_forever()

def export_site(build_dir, static_files_dir, template_dir, locale_dir,
                locale_domain, template_vars):
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    print "copying static files"
    shutil.copytree(static_files_dir, build_dir)
    print "generating locale redirectors"
    redirector = LocaleRedirectorServer(template_dir)
    for dirpath, dirnames, filenames in os.walk(template_dir):
        files = [os.path.join(dirpath, filename)[len(template_dir)+1:]
                 for filename in filenames]
        for relpath in files:
            print "  %s" % (relpath)
            abspath = os.path.join(template_dir, relpath)
            env = {'PATH_INFO': '/%s' % relpath}
            if relpath.endswith('index.html'):
                env['PATH_INFO'] = env['PATH_INFO'][:-len('index.html')]
            mimetype, contents = redirector.handle_file_as_jinja2_template(
                env,
                template_dir,
                abspath
                )
            dest_path = os.path.join(build_dir, relpath)
            mkpath(os.path.dirname(dest_path))
            open(dest_path, 'w').write(contents)
    server = LocalizedTemplateServer(template_dir, locale_dir, locale_domain,
                                     template_vars)
    locales = find_locales(locale_dir, locale_domain, NULL_LOCALE)
    for locale in locales:
        nice_locale = locale.replace('_', '-')
        print "processing localization '%s'" % nice_locale
        env = {}
        server.maybe_apply_translation(env, locale)
        for dirpath, dirnames, filenames in os.walk(template_dir):
            files = [os.path.join(dirpath, filename)[len(template_dir)+1:]
                     for filename in filenames]
            for relpath in files:
                print "  %s/%s" % (nice_locale, relpath)
                abspath = os.path.join(template_dir, relpath)
                mimetype, contents = server.handle_file_as_jinja2_template(
                    env,
                    template_dir,
                    abspath
                    )
                dest_path = os.path.join(build_dir, nice_locale, relpath)
                mkpath(os.path.dirname(dest_path))
                open(dest_path, 'w').write(contents)
    print "done.\n\nyour new static site is located at:\n%s" % build_dir
