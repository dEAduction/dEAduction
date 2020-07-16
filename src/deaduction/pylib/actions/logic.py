from actiondef import action

from dataclasses import dataclass

import deaduction.pylib.logger as logger
import logging


##
# Squelette actions logiques
##

@action("Négation")
def action_negate(goal,):
    log.info("négation")
    return ""

@action("Implication")
def action_implicate(a):
    log.info("implication")
    return ""

@action("Et")
def action_and(a):
    log.info("et")
    return ""

@action("Ou")
def action_or(a):
    log.info("ou")
    return ""

@action("Si et seulement si")
def action_iff(a):
    log.info("si et seulement si")
    return ""

@action("Pour tout")
def action_forall(a):
    log.info("pour tout")
    return ""

@action("Il existe")
def action_exists(a):
    log.info("il existe")
    return ""

if __name__ == "__main__":
    logger.configure()
