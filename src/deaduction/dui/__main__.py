"""
##################
# __main__.py :  #
##################

Author(s)      : - Kryzar <antoine@hugounet.com>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>
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

from deaduction.pylib                            import logger
from deaduction.pylib.server                     import ServerInterface
from deaduction.pylib.config.i18n                import _
import deaduction.pylib.config.dirs              as     cdirs
import deaduction.pylib.config.environ           as     cenv
import deaduction.pylib.config.i18n              as     i18n
import deaduction.pylib.config.site_installation as     inst
import deaduction.pylib.config.vars              as     cvars

#logger.configure(debug=True,
#                 #domains=['ServerInterface', 'deaduction.dui'],
#                 suppress=False)

logger.configure(debug=True,
                 domains=['lean'],
                 suppress=True)

log = logging.getLogger(__name__)


async def main():
    log.debug("starting...")
    test_language = _("Proof by contradiction")
    log.debug(f"Language test: 'Proof by contrapositive' = '{test_language}'")

    #################################################################
    # Init environment variables, directories, and install packages #
    #################################################################
    cenv.init()
    cdirs.init()
    inst.init()

    #############################################################
    # Launch first chooser window  and wait for chosen exercise #
    #############################################################
    exercise = None
    start_coex_startup = StartCoExStartup()
    start_coex_startup.show()

    async with qtrio.enter_emissions_channel(signals=[
            start_coex_startup.exercise_chosen,
            start_coex_startup.window_closed]) as emissions:
        emission = await emissions.channel.receive()
        if emission.is_from(start_coex_startup.exercise_chosen):
            exercise = emission.args[0]
        elif emission.is_from(start_coex_startup.window_closed):
            log.debug("Chooser window closed by user")
            # await emissions.aclose() Inutile ?

    log.debug("Chooser finished")

    #################
    # Infinite loop #
    #################
    while exercise:
        async with trio.open_nursery() as nursery:
            servint = ServerInterface(nursery)
            await servint.start()
            ex_main_window = ExerciseMainWindow(exercise, servint)

            # Show main window, and wait for the "window_closed" signal to
            # happen, so that we can stop the program execution properly.
            try:
                async with qtrio.enter_emissions_channel(
                        signals=[ex_main_window.window_closed]) as emissions:
                    ex_main_window.show()
                    emission = await emissions.channel.receive()
                    cqfd = emission.args[0]
                    log.debug("Exercise window closed by user")
                    if cqfd :
                        log.info("Exercise solved")
            finally:
                log.debug("Waiting for lean's response before stopping...")
                await servint.file_invalidated.wait()
                servint.stop()  # Good job, buddy
                log.debug("Server stopped!")

        #############################
        # Launch new chooser window #
        #############################
        if cqfd:
            start_coex_startup = StartCoExExerciseFinished(exercise)
        else:
            start_coex_startup = StartCoExStartup(exercise)
        start_coex_startup.show()

        async with qtrio.enter_emissions_channel(signals=[
                start_coex_startup.exercise_chosen,
                start_coex_startup.window_closed]) as emissions:
            emission = await emissions.channel.receive()
            if emission.is_from(start_coex_startup.exercise_chosen):
                exercise = emission.args[0]
            elif emission.is_from(start_coex_startup.window_closed):
                exercise = None
                log.debug("Chooser window closed by user")

        log.debug("Chooser finished")


if __name__ == '__main__':
    # list of names of modules whose logs should not be printed
    all_domains = ['lean',
               'ServerInterface',
               'Course',
               'deaduction.dui',
               'deaduction.pylib.coursedata',
               'deaduction.pylib.mathobj'
               ]
    domains = ['lean',
               'ServerInterface',
               'Course',
               'deaduction.pylib.coursedata',
               'deaduction.pylib.mathobj'
               ]
    dui_only = ['deaduction.dui']
    # if suppress=False, only logs from modules in 'domains' will printed
    # if suppress=True, only logs NOT from modules in 'domains' will be printed

    qtrio.run(main)
    log.debug("qtrio finished")
