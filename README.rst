=========
Yaybu.deb
=========

This repository contains a skeleton Debian package that uses dh_virtualenv. This means all the python dependencies are built in. Whilst this is horrible if you are a Debian maintainer it means we can ship newer versions of some of our dependencies than are available in the Debian or Ubuntu archives without affecting other components needing an older version.

To make it super easy to have buildbot precisely control which revision of yay and Yaybu are used the regquirements.txt points at ``src/yay`` and ``src/yaybu``.If you are building by hand you should check out here.
