"""
WSGI config for lg1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import sys
import os
import re
import site

sys.path.append('/var/www/lg1.com/lg1')
site.addsitedir('~/.virtualenvs/django_project_2/local/lib/python2.7/site-packages')

activate_env=os.path.expanduser("/home/ubuntu/.virtualenvs/django_project_2/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

def read_env():
    """Pulled from Honcho code with minor updates, reads local default
    environment variables from a .env file located in the project root
    directory.
 
    """
    try:
        with open('/var/www/lg1.com/lg1/settings_config.env') as f:
            content = f.read()
    except IOError:
        content = ''

    for line in content.splitlines():
        m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
        if m1:
            key, val = m1.group(1), m1.group(2)
            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)
            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r'\\(.)', r'\1', m3.group(1))
            os.environ.setdefault(key, val)

read_env()

os.environ["DJANGO_SETTINGS_MODULE"] =  "lg1.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
