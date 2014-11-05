from flask_debugtoolbar import DebugToolbarExtension

from cla_public.config.dev import *


DEBUG_TB_INTERCEPT_REDIRECTS = False

EXTENSIONS.append(DebugToolbarExtension())
