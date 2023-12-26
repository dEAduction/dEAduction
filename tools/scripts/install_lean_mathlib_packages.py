# Script to install deaduction packages without gui

import deaduction.pylib.config.dirs              as     cdirs
import deaduction.pylib.config.environ           as     cenv
import deaduction.pylib.config.site_installation as     inst

cenv.init()
cdirs.init()
inst.init()

missing_packages = inst.check()

if missing_packages:
    for pkg_name, pkg_desc, pkg_exc in missing_packages:
        pkg_desc.install()