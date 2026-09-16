from . import website
from . import website_sale

# auth_signup is optional. Importing this module only when it is installed keeps
# the addon installable on databases that do not provide signup routes.
try:
    from . import auth_signup
except ImportError:
    pass
