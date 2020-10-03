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
import gettext

from deaduction.dui.launcher import select_course_exercise
from deaduction.dui.widgets import  ExerciseMainWindow
from deaduction.pylib import        logger
from deaduction.pylib.server import ServerInterface

log = logging.getLogger(__name__)

async def main():
    log.debug("starting...")
    # Choose course and exercise
    course, exercise = select_course_exercise()

    if exercise is None:
        raise ValueError(_('Exercise is None'))

    # Init and start server
    async with trio.open_nursery() as nursery:
        servint = ServerInterface(nursery)
        await servint.start()
        ex_main_window = ExerciseMainWindow(exercise, servint)

        # Show main window, and wait for the "window_closed" signal to append,
        # so that we can stop the program execution properly.
        try:
            async with qtrio.enter_emissions_channel(
                    signals=[ex_main_window.window_closed]) as emissions:
                ex_main_window.show()
                await emissions.channel.receive()
        finally:
            servint.stop() # Good job, buddy 


if __name__ == '__main__':
    logger.configure(debug=True)
    _ = gettext.gettext
    qtrio.run(main)
