"""
Using Jinja2 with Django 1.2
Taken from: https://gist.github.com/472309
Based on: http://djangosnippets.org/snippets/2063/

To use:
  * Add this template loader to settings: `TEMPLATE_LOADERS`
  * Add template dirs to settings: `JINJA2_TEMPLATE_DIRS`

If in template debug mode - we fire the template rendered signal, which allows
debugging the context with the debug toolbar.  Viewing source currently doesnt
work.
"""

import jinja2
import simplejson
from django.template.loader import BaseLoader
from django.template import TemplateDoesNotExist, Origin
from django.core.context_processors import csrf as django_csrf
from django.core import urlresolvers
from django.conf import settings
from crimpyutils.django_jinja.jinja2htmlcompress import SelectiveHTMLCompress


# Global functions
# -------------------------

def reverse_account_url(viewname, request=None, urlconf=None, args=None, kwargs=None, prefix=None, current_app=None):
    """Convenience function for URLs with an account prefix."""
    if request:
        if kwargs:
            kwargs['account_slug'] = request.account.slug
        else:
            kwargs = {'account_slug': request.account.slug}
    return urlresolvers.reverse(viewname, urlconf, args, kwargs, prefix, current_app)

def csrf(request):
    """Generate a CSRF token."""
    return django_csrf(request)['csrf_token']


# Custom filters
# -------------------------

def pluralize(value, plural_suffix="s", singular_suffix=""):
    if isinstance(value, (int, float, long)):
        if value == 1:
            return singular_suffix
        else:
            return plural_suffix
    else:
        if len(value) == 1:
            return singular_suffix
        else:
            return plural_suffix

def json_dumps(value, indent=4):
    return simplejson.dumps(value, indent=indent)


# Django/Jinja integration
# -------------------------

class Template(jinja2.Template):
    def render(self, context):
        # flatten the Django Context into a single dictionary.
        context_dict = {}
        for d in context.dicts:
            context_dict.update(d)
        
        if settings.TEMPLATE_DEBUG:
            from django.test import signals
            self.origin = Origin(self.filename)
            signals.template_rendered.send(sender=self, template=self, context=context)
        
        return super(Template, self).render(context_dict)

class Loader(BaseLoader):
    """
    A file system loader for Jinja2.
    
    Requires the following setting `JINJA2_TEMPLATE_DIRS`
    """
    is_usable = True

    def __init__(self, *args, **kwargs):
        super(Loader, self).__init__(*args, **kwargs)

        # Set up the jinja env and load any extensions you may have
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(settings.JINJA2_TEMPLATE_DIRS),
            extensions=(SelectiveHTMLCompress,)
        )
        self.env.template_class = Template

        # add global identifiers
        self.env.globals['url'] = urlresolvers.reverse
        self.env.globals['settings'] = settings
        self.env.globals['csrf'] = csrf
        self.env.globals['debug'] = settings.DEBUG
        self.env.globals.update(self.more_globals())

        # add custom filters
        self.env.filters['pluralize'] = pluralize
        self.env.filters.update(self.more_filters())

    def more_globals(self):
        return {}

    def more_filters(self):
        return {}

    def load_template(self, template_name, template_dirs=None):
        try:
            template = self.env.get_template(template_name)
            return template, template.filename
        except jinja2.TemplateNotFound:
            raise TemplateDoesNotExist(template_name)
