import deaduction.pylib.logger as logger
import logging

import re

def test_basic(capsys):
    # date/time information is masked with regex numbers
    RESP = re.compile( r"\d{4}-\d+-\d+ \d+:\d+:\d+,\d+ DEBUG    : This is debug\n"   \
                       r"\d{4}-\d+-\d+ \d+:\d+:\d+,\d+ INFO     : This is info\n"    \
                       r"\d{4}-\d+-\d+ \d+:\d+:\d+,\d+ WARNING  : This is warning\n" \
                       r"\d{4}-\d+-\d+ \d+:\d+:\d+,\d+ ERROR    : This is error\n"   \
                       r"\d{4}-\d+-\d+ \d+:\d+:\d+,\d+ CRITICAL : This is broken\n"  )

    logger.configure()

    log = logging.getLogger("logger test")

    log.debug    ("This is debug"  )
    log.info     ("This is info"   )
    log.warning  ("This is warning")
    log.error    ("This is error"  )
    log.critical ("This is broken" )

    captured = capsys.readouterr()
    assert RESP.match(captured.err)
