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

from deaduction.dui.stages.exercise              import ExerciseMainWindow
from deaduction.dui.stages.start_coex            import StartCoExStartup, \
                                            StartCoExExerciseFinished

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


async def main():
    """
    Main event loop. Alternatively launch the two main windows, i.e.
        - Course/Exercise chooser window,
        - Exercise window
    """

    log.info("Starting...")

    #################################################################
    # Init environment variables, directories, and install packages #
    #################################################################
    cenv.init()
    cdirs.init()
    inst.init()

    #############################################################
    # Launch first chooser window  and wait for chosen exercise #
    #############################################################
    chosen_exercise = None
    start_coex_startup = StartCoExStartup()
    start_coex_startup.show()

    async with qtrio.enter_emissions_channel(signals=[
            start_coex_startup.exercise_chosen,
            start_coex_startup.window_closed]) as emissions:
        emission = await emissions.channel.receive()
        if emission.is_from(start_coex_startup.window_closed):
            # d∃∀duction will stop.
            log.debug("Chooser window closed by user")
        elif len(emission.args) > 0 and isinstance(emission.args[0], Exercise):
            chosen_exercise = emission.args[0]

    #################
    # Infinite loop #
    #################
    while chosen_exercise:
        async with trio.open_nursery() as nursery:
            # Start Lean server.
            servint = ServerInterface(nursery)
            await servint.start()

            # Show main window, and wait for the "window_closed" signal to
            # happen, so that we can stop the program execution properly.
            ex_main_window = ExerciseMainWindow(chosen_exercise, servint)
            try:
                # Wait for exercise window closed.
                signals = [ex_main_window.window_closed]
                async with qtrio.enter_emissions_channel(signals=signals) \
                        as emissions:
                    ex_main_window.show()
                    emission = await emissions.channel.receive()
                    cqfd = emission.args[0]  # True iff exercise solved
                    log.debug("Exercise window closed by user")
                    if cqfd:
                        log.info("Exercise solved")
            finally:
                log.debug("Waiting for lean's response before stopping...")
                await servint.file_invalidated.wait()
                servint.stop()  # Good job, buddy
                # TODO: close the nursery!
                log.debug("Server stopped!")
                nursery.cancel_scope.cancel()

        #############################
        # Launch new chooser window #
        #############################
        if cqfd:
            # Display fireworks inside course/exercise chooser.
            start_coex_startup = StartCoExExerciseFinished(chosen_exercise)
        else:
            start_coex_startup = StartCoExStartup(chosen_exercise)
        start_coex_startup.show()

        # Wait for either chooser window closed or exercise chosen.
        signals = [start_coex_startup.exercise_chosen,
                   start_coex_startup.window_closed]
        async with qtrio.enter_emissions_channel(signals=signals) as emissions:
            emission = await emissions.channel.receive()
            if emission.is_from(start_coex_startup.window_closed):
                chosen_exercise = None
                log.debug("Chooser window closed by user")
                # d∃∀duction will stop.
            elif len(emission.args) > 0 and isinstance(emission.args[0],
                                                       Exercise):
                chosen_exercise = emission.args[0]

if __name__ == '__main__':
    qtrio.run(main)
    log.debug("qtrio finished")
