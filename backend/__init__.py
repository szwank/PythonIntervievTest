import os
import sys
import inspect

[sys.path.insert(0, path) for path in [
    ".",
    os.path.join("backend", "lib")
] if path not in sys.path]


def include_paths():
    root = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), "..")

    return [
        os.path.join(root, "backend", "lib"),
        os.path.join(root, "node_modules", "appengine-python-sdk", "google_appengine"),
        os.path.join(root, "node_modules", "appengine-python-sdk", "google_appengine", "lib", "webapp2-2.5.2"),
        os.path.join(root, "node_modules", "appengine-python-sdk", "google_appengine", "lib", "webob-1.2.3"),
        os.path.join(root, "node_modules", "appengine-python-sdk", "google_appengine", "lib", "yaml-3.10"),
        os.path.join(root, "node_modules", "appengine-python-sdk", "google_appengine", "lib", "fancy_urllib"),
        os.path.join(root, "node_modules", "appengine-python-sdk", "google_appengine", "lib", "pyasn1"),  # NOTE: only needed for deplyment. move to appcfg?
        os.path.join(root, "node_modules", "appengine-python-sdk", "google_appengine", "lib", "pyasn1_modules"),  # NOTE: only needed for deplyment. move to appcfg?
        os.path.join(root, "node_modules", "appengine-python-sdk", "google_appengine", "lib", "rsa")  # NOTE: only needed for deplyment. move to appcfg?
    ]
