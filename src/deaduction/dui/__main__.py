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

import logging
import qtrio
import trio
from PySide2.QtCore import (                     QObject,
                                                 Signal,
                                                 Slot)

from deaduction.dui.stages.exercise              import ExerciseMainWindow
from deaduction.dui.stages.start_coex            import StartCoExStartup

from deaduction.pylib.coursedata                 import Exercise
from deaduction.pylib                            import logger
from deaduction.pylib.server                     import ServerInterface
import deaduction.pylib.config.dirs              as     cdirs
import deaduction.pylib.config.environ           as     cenv
import deaduction.pylib.config.site_installation as     inst

logger.configure(debug=True,
                 domains=['lean'],
                 suppress=True)

log = logging.getLogger(__name__)


###############################################
# Container class, managing signals and slots #
###############################################
class Container(QObject):
    """
    This class  is responsible for keeping the memory of open windows
    (chooser window and exercise window), launching the windows when needed,
    and connecting relevant signals (when windows are closed, when a new
    exercise is chosen, or when user wants to change exercise) to the
    corresponding launching methods. Note that in PyQt signals have to be
    hosted by a QObject.
    """

    close_chooser_window = Signal()
    close_exercise_window = Signal()

    def __init__(self, nursery):
        super().__init__()

        self.exercise_window:   ExerciseMainWindow       = None
        self.chooser_window:    StartCoExStartup         = None
        self.servint:           ServerInterface          = None
        self.exercise:          Exercise                 = None
        self.nursery:           trio.Nursery             = nursery

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

        # Start Lean server
        self.servint = ServerInterface(self.nursery)
        await self.servint.start()

        # Start exercise window
        self.exercise_window = ExerciseMainWindow(self.exercise, self.servint)

        # Connect signals
        self.exercise_window.window_closed.connect(self.close_exercise_window)
        self.exercise_window.change_exercise.connect(self.choose_exercise)

        # Show window
        self.exercise_window.show()


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
