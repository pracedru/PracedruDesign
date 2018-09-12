import os
import sipconfig
# from PyQt5 import QtCore

home_dir = os.path.expanduser('~')
sip_inc_dir = "/usr/share/sip/PyQt5"
qt_inc_dir = "/usr/include/x86_64-linux-gnu/qt5"   # Ubuntu
#qt_inc_dir = "/usr/include/qt5"  # OpenSuse

target_sip_file = "NurbSurfer.sip"
target_lib_dir = home_dir + "/QtProjects/build-NurbSurfer-Desktop-Debug"
target_inc_dir = home_dir + "/QtProjects/NurbSurfer"

build_file = "NurbSurfer.sbf"

config = sipconfig.Configuration()

#os.system(" ".join([config.sip_bin, "-c", ".", "-b", build_file, "-I" + sip_inc_dir, QtCore.PYQT_CONFIGURATION["sip_flags"], "nurbsurfer.sip"]))
#  -n PyQt5.sip (from QtCore.PYQT_CONFIGURATION["sip_flags"]) does not work with my current sip version.

os.system(" ".join([config.sip_bin, "-c", ".", "-b", build_file, "-I" + sip_inc_dir, "-t WS_X11", target_sip_file]))

makefile = sipconfig.SIPModuleMakefile(config, build_file)

extraFlags = "-std=c++11 -I%s -I%s/QtCore -I%s/QtGui -I%s" % (qt_inc_dir, qt_inc_dir, qt_inc_dir, target_inc_dir)
makefile.extra_cflags = [extraFlags]
makefile.extra_cxxflags = [extraFlags]
makefile.extra_lflags = ["-Wl,-R" + target_lib_dir]
makefile.extra_lib_dirs = [target_lib_dir]
makefile.extra_libs = ["NurbSurfer"]

makefile.generate()