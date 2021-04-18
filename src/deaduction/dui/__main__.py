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

import ctypes
import logging
import qtrio
import threading
import trio

from PySide2.QtCore import ( QObject,
                             Signal,
                             Slot  )

from deaduction.dui.stages.exercise              import ExerciseMainWindow
from deaduction.dui.stages.start_coex            import StartCoExStartup

from deaduction.dui.stages.missing_dependencies  import (InstallingMissingDependencies,
                                                         WantInstallMissingDependencies )

from deaduction.pylib.coursedata                 import Exercise
from deaduction.pylib                            import logger
from deaduction.pylib.server                     import ServerInterface

import deaduction.pylib.config.dirs              as     cdirs
import deaduction.pylib.config.environ           as     cenv
import deaduction.pylib.config.site_installation as     inst
import deaduction.pylib.config.vars              as     cvars

# (non-exhaustive) list of logger domains:
# ['lean', 'ServerInterface', 'Course', 'deaduction.dui',
#  'deaduction.pylib.coursedata', 'deaduction.pylib.mathobj', 'LeanServer']

###################
# Configuring log #
###################
# Change your own settings in .deaduction-dev/config.toml
log_domains = cvars.get("logs.domains", "")

log_domains = ["deaduction", "__main__", 'ServerInterface', 'magic']
log_level = cvars.get("logs.display_level", 'info')
# log_domains = ""
log_level = 'debug'
logger.configure(domains=log_domains,
                 display_level=log_level)

log = logging.getLogger(__name__)

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
        self.thread                = threading.Thread(target=self.do_install, daemon=True)

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
            for pkg_name,pkg_desc,pkg_exc in self.missing_packages:
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
class Container(QObject):
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

    close_chooser_window  = Signal()
    close_exercise_window = Signal()
    server_started        = Signal()
    test_complete         = Signal()  # For testing only

    def __init__(self, nursery, exercise=None):
        super().__init__()

        self.exercise_window: ExerciseMainWindow = None
        self.chooser_window:  StartCoExStartup   = None
        self.servint:         ServerInterface    = None
        self.exercise:        Exercise           = exercise
        self.nursery:         trio.Nursery       = nursery
        self.exercises:       [Exercise]         = []
        self.auto_test:       bool               = False
        self.report:          [[str]]            = []

    @Slot()
    def choose_exercise(self):
        """
        Launch chooser window and connect signals. This is the first method
        that will be called by main().
        """

        log.debug("Choosing new exercise")
        if not self.chooser_window:
            # Start chooser window
            self.chooser_window = StartCoExStartup(exercise=self.exercise)

            # Connect signals
            self.chooser_window.exercise_chosen.connect(self.start_exercise)
            self.chooser_window.window_closed.connect(
                                                self.close_chooser_window)
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
        Just a synchronous front-end to the async method solve_exercise
        (apparently slots may not be asynchronous functions).
        """

        self.chooser_window = None  # So that exiting d∃∀duction works
        self.exercise = exercise
        if self.exercise_window:
            # Close window but do not tell main() since a new exercise
            # window will be launched immediately!!
            self.exercise_window.window_closed.disconnect()
            self.exercise_window.close()

        self.nursery.start_soon(self.solve_exercise)

    async def solve_exercise(self):
        """
        Launch exercise window, start lean server, and connect signals.
        """

        log.debug(f"Starting exercise {self.exercise.pretty_name}")

        # Stop Lean server if running
        if self.servint:
            await self.servint.file_invalidated.wait()
            self.servint.stop()
            log.info("Lean server stopped!")

        # Start Lean server
        self.servint = ServerInterface(self.nursery)
        await self.servint.start()
        log.info("Lean server started")

        # Start exercise window
        self.exercise_window = ExerciseMainWindow(self.exercise, self.servint)

        # Connect signals
        self.exercise_window.window_closed.connect(self.close_exercise_window)
        self.exercise_window.change_exercise.connect(self.choose_exercise)

        # Show window
        self.exercise_window.show()

    async def test_exercise(self):
        """
        Launch exercise window, start lean server, and connect signals
        for testing self.exercise. Very much like solve_exercise, except for
        - setting auto_steps,
        - connecting proof_no_goal signal to test_complete.
        """

        # TODO: box for cancelling auto_test (reprendre la main)
        log.debug(f"Preparing {self.exercise.pretty_name} for test")

        # Stop Lean server if running
        if self.servint:
            await self.servint.file_invalidated.wait()
            self.servint.stop()
            log.info("Lean server stopped!")

        # Start Lean server
        self.servint = ServerInterface(self.nursery)
        await self.servint.start()
        log.info("Lean server started")
        self.server_started.emit()

        # Start exercise window and add auto_steps
        self.exercise_window = ExerciseMainWindow(self.exercise, self.servint)
        # self.exercise_window.auto_steps = self.exercise.refined_auto_steps

        # Connect signals
        self.exercise_window.window_closed.connect(self.close_exercise_window)
        self.servint.proof_no_goals.connect(self.test_complete)
        # The following avoid QMessageBox in firework and when goal solved
        self.exercise_window.cqfd = True

        # Show window
        self.exercise_window.show()

    @Slot()
    def quit_deaduction(self):
        if self.exercise_window:
            self.exercise_window.close()
            # Just in case signal is disconnected
            self.close_exercise_window.emit()
        if self.chooser_window:
            self.chooser_window.close()
            self.close_chooser_window.emit()


##############################################################
# Main event loop: init container and wait for window closed #
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

        # Create container
        container = Container(nursery)
        # Choose first exercise
        container.choose_exercise()

        # Main loop that just listen to closing windows signals,
        # and quit if there is no more open windows.
        signals = [container.close_chooser_window,
                   container.close_exercise_window]
        try:
            async with qtrio.enter_emissions_channel(signals=signals) as \
                    emissions:
                async for emission in emissions.channel:
                    log.debug("Signal received")
                    if emission.is_from(container.close_chooser_window):
                        # Remember that there is no more chooser window:
                        container.chooser_window = None
                        log.debug("No more chooser window")
                    elif emission.is_from(container.close_exercise_window):
                        # Remember that there is no more exercise window:
                        container.exercise_window = None
                        log.debug("No more exercise window")

                    # Quit if no more open window:
                    if not (container.chooser_window or
                            container.exercise_window):
                        log.debug("Closing d∃∀duction")
                        break
                # log.debug("Out of async for loop")
            # log.debug("Out of async with")
        finally:
            # Finally closing d∃∀duction
            if container.servint:
                await container.servint.file_invalidated.wait()
                container.servint.stop()  # Good job, buddy
                log.info("Lean server stopped!")
            if container.nursery:
                container.nursery.cancel_scope.cancel()


if __name__ == '__main__':
    log.info("Starting...")
    #################################################################
    # Init environment variables, directories, and install packages #
    #################################################################

    cenv.init()
    cdirs.init()
    inst.init()

    qtrio.run(main)
    log.debug("qtrio finished")
