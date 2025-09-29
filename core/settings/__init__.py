import os

MODE_SETTINGS = os.getenv("MODE_SETTINGS", "development")

if MODE_SETTINGS == 'production':
    from .production import *
else:
    from .development import *