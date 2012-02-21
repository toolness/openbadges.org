This is the content for the website at [openbadges.org][].

  [openbadges.org]: http://openbadges.org

## Prerequisites

You need Python version 2.6 or higher. All other dependencies are
self-contained within the project's code repository.

## Setup

Just run this at the terminal prompt:

    cd openbadges.org
    python manage.py runserver

Then, point your browser to http://localhost:8000/.

## Development

All static, unlocalized files are in the `static` directory, which are
placed at the root of the web site. The `templates` directory
contains localized [Jinja2][] templates that are located at `/<locale>/` on
the web site, where `<locale>` is the name of a locale like `en-US`. The
single exception to this is the file `templates/locale-redirector.html`,
which is used to redirect a non-localized pathname to a localized one (e.g.,
redirecting `/goggles/` to `/en-US/goggles`).

Whenever you need to link to a localized template, you can do so either via
a relative URL or an absolute one that begins with the template variable
`{{ LOCALE_ROOT }}`.

  [Jinja2]: http://jinja.pocoo.org/

## Testing

When writing JavaScript code, please try to make it testable and add
a unit test for it in the `static/test` directory. These [QUnit][]
tests can be run from the development server at  [localhost:8000/test][].

  [QUnit]: http://docs.jquery.com/Qunit
  [localhost:8000/test]: http://localhost:8000/test/

## Localization

The site uses GNU gettext for localization via [Babel][] and Jinja2's
[i18n extension][]. Soon we'll get the site listed on
[localize.mozilla.org][] so that anyone can easily help localize
the website.

  [Babel]: http://babel.edgewall.org/
  [i18n extension]: http://jinja.pocoo.org/docs/templates/#extensions
  [localize.mozilla.org]: https://localize.mozilla.org

## Deployment

Run this at the terminal prompt:

    python manage.py build
    
This will create a static version of the site, for all supported locales, in 
the `dist` directory. You can copy this directory to any web server that 
serves static files, such as Apache or Amazon S3.

## Technical Design Philosophy

The Open Badges website is almost entirely static content, so we didn't see
much of a need to use a massive server-side framework like [Playdoh][].
Instead, we took an approach more akin to that of [Jekyll][], whereby
a script can be run to generate a fully static site capable of being
deployed to any static web server.

However, we pick from Playdoh's toolkit when we need to solve a problem, which
results in a code repository that looks more familiar to Mozilla developers as
the site's requirements become more complex.

  [Playdoh]: https://github.com/mozilla/playdoh
  [Jekyll]: https://github.com/mojombo/jekyll/wiki
