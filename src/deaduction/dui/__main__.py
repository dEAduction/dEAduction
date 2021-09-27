"""
##################
# __main__.py :  #
##################

Author(s)      : - Kryzar <antoine@hugounet.com>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>
                 - Frédéric Le Roux <frederic.le-roux@imj-prg.fr>

Maintainers(s) : - Kryzar <antoine@hugounet.com>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : July 2020

Copyright (c) 2020 the dEAduction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    d∃∀duction is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with d∃∀duction. If not, see <https://www.gnu.org/licenses/>.
"""

from sys import argv
import logging
import qtrio
import threading
import trio
import argparse
import os

from PySide2.QtCore import ( QObject,
                             Signal,
                             Slot  )

import deaduction.pylib.config.dirs              as     cdirs
import deaduction.pylib.config.environ           as     cenv
import deaduction.pylib.config.site_installation as     inst
import deaduction.pylib.config.vars              as     cvars
###################
# ! DO NOT MOVE ! #
###################
# i18n has to be executed BEFORE translation function "_" is used.
import deaduction.pylib.config.i18n

from deaduction.dui.stages.select_language       import select_language
from deaduction.dui.stages.exercise              import Coordinator
from deaduction.dui.stages.start_coex            import StartCoExStartup
from deaduction.dui.stages.missing_dependencies  import (
                InstallingMissingDependencies, WantInstallMissingDependencies)
from deaduction.dui.stages.test                  import QTestWindow
from deaduction.pylib.coursedata                 import Exercise
from deaduction.pylib                            import logger
from deaduction.pylib.server                     import ServerInterface
from deaduction.pylib.autotest import                   select_exercise

# (non-exhaustive) list of logger domains:
# ['lean', 'ServerInterface', 'ServerQueue', 'Course', 'deaduction.dui',
#  'deaduction.pylib.coursedata', 'deaduction.pylib.mathobj', 'LeanServer']

###################
# Configuring log #
###################
# Change your own settings in .deaduction-dev/config.toml
log_domains = cvars.get("logs.domains", "")
log_level = cvars.get("logs.display_level", 'info')

if os.getenv("DEADUCTION_DEV_MODE", False):
    log_level = 'debug'
    log_domains = ["deaduction", "__main__",  # 'lean',
                   'ServerInterface', 'ServerQueue']
    log_domains = ["__main__",
                   'ServerInterface',
                   'ServerQueue',
                   'lean',
                   'deaduction.dui',
                   'deaduction.pylib',
                   'logic',
                   'magic']


logger.configure(domains=log_domains,
                 display_level=log_level)

log = logging.getLogger(__name__)

###########################
# Configuring args parser #
###########################

arg_parser = argparse.ArgumentParser("Start deaduction graphical interface "
                                     "for Lean theorem prover")
arg_parser.add_argument('--course', '-c', help="Course filename")
arg_parser.add_argument('--exercise', '-e', help="Exercise (piece of) name")


############################
# Check dependencies stage #
############################
class Install_Dependencies_Stage(QObject):
    install_completed = Signal()
    start_deaduction  = Signal()

    def __init__(self, nursery, missing_packages):
        super().__init__()

        self.nursery: trio.Nursery = nursery
        self.missing_packages      = missing_packages

        self.install_dialog        = InstallingMissingDependencies()
        self.thread                = threading.Thread(target=self.do_install,
                                                      daemon=True)

        # Connect log display
        self.install_dialog.log_attach(logging.getLogger(""))

        # Connect
        self.install_dialog.plz_start_deaduction.connect(self.plz_start_deaduction)
        self.install_dialog.plz_quit.connect(self.plz_quit)

        self.install_completed.connect(self.install_dialog.installation_completed)

    def start(self):
        # Show dialog, start thread
        self.install_dialog.log_start()

        self.install_dialog.show()
        self.thread.start()

    def stop(self):
        self.thread.join()

        self.install_dialog.log_stop()
        self.install_dialog.log_dettach(logging.getLogger(""))
        self.install_dialog.close()

    def do_install(self):
        try:
            for pkg_name, pkg_desc, pkg_exc in self.missing_packages:
                pkg_desc.install()
        finally:
            self.install_completed.emit()

    @Slot()
    def plz_quit(self):
        raise SystemExit()

    @Slot()
    def plz_start_deaduction(self):
        self.start_deaduction.emit()


async def site_installation_check(nursery):
    missing_packages = inst.check()
    
    if missing_packages:
        want_install_dialog = WantInstallMissingDependencies(map(lambda x: x[0], missing_packages))
        want_install_dialog.exec_()

        if want_install_dialog.yes:
            inst_stg = Install_Dependencies_Stage(nursery, missing_packages)
            async with qtrio.enter_emissions_channel(signals=[inst_stg.start_deaduction]) as \
                       emissions:

                inst_stg.start()
                async for emission in emissions.channel:
                    if emission.is_from(inst_stg.start_deaduction):
                        break
                inst_stg.stop()


###############################################
# Container class, managing signals and slots #
###############################################
class WindowManager(QObject):
    """
    This class is responsible for keeping the memory of open windows
    (CoEx starter and exercise window), launching the windows when
    needed, and connecting relevant signals (when windows are closed,
    when a new exercise is chosen, or when user wants to change
    exercise) to the corresponding launching methods. Note that in PyQt
    signals have to be hosted by a QObject.

    :attribute exercises: list of exercises to be launched one after another
    without asking user. Useful for testing.
    """

    chooser_window_closed  = Signal()
    exercise_window_closed = Signal()
    server_started        = Signal()
    # proof_complete        = Signal()  # For testing only
    test_complete         = Signal()  # For testing only

    def __init__(self, nursery, exercise=None):
        super().__init__()

        self.coordinator: Coordinator            = None
        self.chooser_window:  StartCoExStartup   = None
        self.servint:         ServerInterface    = None
        self.test_window:     QTestWindow        = None
        self.exercise:        Exercise           = exercise
        self.nursery:         trio.Nursery       = nursery
        self.exercises:       [Exercise]         = []
        self.auto_test:       bool               = False
        self.report:          [[str]]            = []

    @property
    def exercise_window(self):
        if self.coordinator:
            return self.coordinator.emw
        else:
            return None

    async def check_lean_server(self):
        """
        Check for ServerInterface, and if none, start a new one.
        """
        if not self.servint:
            self.servint = ServerInterface(self.nursery)
        if not self.servint.lean_server_running.is_set():
            await self.servint.start()
            log.info("Lean server started")

    ###################################
    # Methods corresponding to stages #
    ###################################
    @Slot()
    def choose_exercise(self):
        """
        Launch chooser window and connect signals. This is the first method
        that will be called by main().
        """

        log.info("Choosing new exercise")

        if not self.chooser_window:
            # Start chooser window
            self.chooser_window = StartCoExStartup(exercise=self.exercise,
                                                   servint=self.servint)

            # Connect signals
            self.chooser_window.exercise_chosen.connect(self.start_exercise)
            self.chooser_window.window_closed.connect(
                                                self.chooser_window_closed)
            self.chooser_window.quit_deaduction.connect(self.quit_deaduction)

            # Show window
            self.chooser_window.show()
        else:
            # Focus on chooser window
            self.chooser_window.raise_()
            self.chooser_window.activateWindow()

    @Slot()
    def start_exercise(self, exercise):
        """
        Just a front-end to the solve_exercise method.
        """
        # TODO: might be merged with solve_exercise, no more async
        #  but cf tests
        self.chooser_window = None  # So that exiting d∃∀duction works
        self.exercise = exercise
        if self.exercise_window:
            # Close window but do not tell main() since a new exercise
            # window will be launched immediately!!
            try:
                self.exercise_window.window_closed.disconnect()
                self.exercise_window.close()
            except RuntimeError:
                pass
        # Do start exercise!
        self.solve_exercise()

    def solve_exercise(self):
        """
        Launch exercise window and connect signals.
        """

        log.debug(f"Starting exercise {self.exercise.pretty_name}")

        # Start coordinator, who will start an ExerciseMainWindow instance
        self.coordinator = Coordinator(self.exercise, self.servint)

        # Connect signals
        self.exercise_window.window_closed.connect(self.exercise_window_closed)
        self.exercise_window.change_exercise.connect(self.choose_exercise)

        # Show window
        self.exercise_window.show()

    def test_exercise(self, test_window):
        """
        Launch exercise window, start lean server, and connect signals
        for testing self.exercise. Very much like solve_exercise, except for
        - setting test_mode,
        - connecting proof_no_goal signal to test_complete.
        """
        # FIXME: adapt to new methods!!
        # TODO: box for cancelling auto_test (reprendre la main)
        log.debug(f"Preparing {self.exercise.pretty_name} for test")

        # Start exercise window and test window
        self.coordinator = Coordinator(self.exercise, self.servint)
        self.test_window = test_window
        self.test_window.show()
        self.exercise_window.test_mode = True
        self.coordinator.test_mode = True

        # Connect signals
        self.exercise_window.window_closed.connect(self.exercise_window_closed)
        # self.coordinator.proof_no_goals.connect(self.proof_complete)

        # Show exercise window
        self.exercise_window.show()

    @Slot()
    def quit_deaduction(self):
        if self.exercise_window:
            self.exercise_window.close()
            # Just in case signal is disconnected
            self.exercise_window_closed.emit()
        if self.chooser_window:
            self.chooser_window.close()
            self.chooser_window_closed.emit()


def exercise_from_argv() -> Exercise:
    """
    Try to build Exercise object from arguments.
    """
    exercise = None
    args = arg_parser.parse_args(argv[1:])
    course_path = args.course
    exercise_like = args.exercise

    if course_path and exercise_like:
        log.debug('Searching course and exercise...')
        course, exercise = select_exercise(course_path, exercise_like)

    return exercise


##############################################################
# Main event loop: init wm and wait for window closed #
##############################################################
async def main():
    """
    This is the main loop. It opens a trio.nursery, instantiate a Container
    for signals and slots, and call the Container.choose_exercise method.
    Then it listens to signals emitted when windows are closed, and decides
    to quit when all windows are closed. Quitting implies stopping the lean
    server that may be running and closing the trio's nursery.
    """

    async with trio.open_nursery() as nursery:
        await site_installation_check(nursery)

        # Create wm and start Lean server
        wm = WindowManager(nursery)
        await wm.check_lean_server()

        try:
            # Choose first exercise
            exercise = exercise_from_argv()
            if not exercise:
                wm.choose_exercise()
                # wm.choose_exercise()
            else:
                wm.start_exercise(exercise)
            # Main loop that just listen to closing windows signals,
            # and quit if there is no more open windows.
            signals = [wm.chooser_window_closed,
                       wm.exercise_window_closed]
            async with qtrio.enter_emissions_channel(signals=signals) as \
                    emissions:
                async for emission in emissions.channel:
                    # log.debug("Signal received")
                    if emission.is_from(wm.chooser_window_closed):
                        # Remember that there is no more chooser window:
                        wm.chooser_window = None
                        log.debug("No more chooser window")
                    elif emission.is_from(wm.exercise_window_closed):
                        # Remember that there is no more exercise window:
                        wm.coordinator.emw = None
                        log.debug("No more exercise window")

                    # Quit if no more open window:
                    if not (wm.chooser_window or
                            wm.exercise_window):
                        log.debug("Closing d∃∀duction")
                        break
        finally:
            # Properly close d∃∀duction
            if wm.servint:
                with trio.move_on_after(10):
                    await wm.servint.file_invalidated.wait()
                wm.servint.stop()  # Good job, buddy
                log.info("Lean server stopped!")
            if wm.nursery:
                wm.nursery.cancel_scope.cancel()


if __name__ == '__main__':
    log.info("Starting...")
    #################################################################
    # Init environment variables, directories, and install packages #
    #################################################################

    cenv.init()
    cdirs.init()
    inst.init()

    ############################
    # First choice of language #
    ############################
    language = deaduction.pylib.config.i18n.init_i18n()
    if language == "no_language":
        selected_language, ok = select_language()
        if not selected_language:
            selected_language = 'en'
        cvars.set('i18n.select_language', selected_language)
        deaduction.pylib.config.i18n.init_i18n()
        if ok:
            cvars.save()  # Do not ask next time!

    #################
    # Run main loop #
    #################
    qtrio.run(main)
    log.debug("qtrio finished")
