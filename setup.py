import os
import sys
import pkg_resources
import pkgutil
import shutil
import distutils
import glob

import cx_Freeze
import cx_Freeze.freezer
from cx_Freeze import setup, hooks, Executable

sys.modules['cx_Freeze.freezer'].EXTENSION_LOADER_SOURCE = \
"""
def __bootstrap__():
    imp = __import__("imp")
    os = __import__("os")
    sys = __import__("sys")
    global __bootstrap__, __loader__
    __loader__ = None; del __bootstrap__, __loader__

    found = False
    for p in sys.path:
        if not os.path.isdir(p):
            continue
        f = os.path.join(p, "%s")
        if not os.path.exists(f):
            continue
        m = imp.load_dynamic(__name__, f)
        import sys
        sys.modules[__name__] = m
        found = True
        break
    if not found:
        del sys.modules[__name__]
        raise ImportError("No module named %%s" %% __name__)
__bootstrap__()
"""

def load_requests(finder, module):
    """ the requests library needs cacert.pem """
    fileName = os.path.join(module.path[0], "cacert.pem")
    finder.IncludeFiles(fileName, os.path.basename(fileName))
hooks.load_requests = load_requests


class build_exe(cx_Freeze.build_exe):

    def setup_env(self):
        if os.path.exists(self.build_exe):
            print "*** removing build dir ***"
            shutil.rmtree(self.build_exe)

        self.work_dir = "work.%s-%s" % (distutils.util.get_platform(), sys.version[0:3])
        if os.path.exists(self.work_dir):
            print "*** removing work dir ***"
            shutil.rmtree(self.work_dir)

        os.makedirs(self.work_dir)

    def generate_fake_eggs(self):
        includes = []

        print "*** generating fake egg metadata ***"
        eggs = pkg_resources.require("Yaybu")
        for egg in eggs:
            print '%s == %s' % (egg.project_name, egg.version)
            path = os.path.join(self.work_dir, '%s.egg-info' % egg.project_name)
            with open(path, "w") as fp:
                fp.write("Metadata-Version: 1.0\n")
                fp.write("Name: %s\n" % egg.project_name)
                fp.write("Version: %s\n" % egg.version)

            includes.append((path, os.path.basename(path)))

        self.include_files.extend(includes)

    def _extend_library_zip(self, package, globs):
        src = pkgutil.get_loader(package).filename
        assert os.path.isdir(src), "'%s' must resolve to a folder" % package

        for g in globs:
            for f in glob.glob(os.path.join(src, g)):
                rel = os.path.join(
                    os.path.join(*package.split(".")),
                    os.path.relpath(f, src),
                )
                self.zip_includes.append((f, rel))

    def bundle_test_assets(self):
        print "*** Bundling test assets ***"
        self._extend_library_zip('yaybu.tests', ('*.json', 'assets/*'))

    def run(self):
        self.setup_env()
        self.generate_fake_eggs()
        self.bundle_test_assets()
        return cx_Freeze.build_exe.run(self)


setup(
    name = "Yaybu",
    version = "0.1",
    options = {
        "build_exe": {
            "packages": [
                "yaybu",
            ],
        },
    },
    executables = [
        Executable("shell.py", targetName="yaybu"),
    ],
    cmdclass = {
        'build_exe': build_exe,
    },
)
