"""
"""

from dataclasses import dataclass
from actiondef   import action

############################################
# Examples actions
############################################
@action("Négation")
def negate(a):
    print("négation", a)

@action("Implication")
def implicate(a):
    print("implication", a)

@action("test")
def test(a):
    print("test", a)
