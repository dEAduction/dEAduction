"""
# __init__.py : #ShortDescription #
    
    https://en.meming.world/images/en/8/8e/All_Right_Then%2C_Keep_Your_Secrets.jpg

Author(s)     : Marguerite Bin bin.marguerite@gmail.com
Maintainer(s) : Marguerite Bin bin.marguerite@gmail.com
Created       : 07 2020 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

This file is part of dEAduction.

    dEAduction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    dEAduction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

from .actiondef import (    Action,
                            action)

from .exceptions import (   InputType,
                            MissingParametersError,
                            WrongUserInput)

from .utils import (        get_new_hyp,
                            get_new_var,
                            format_orelse)

from .logic import (        action_negate,
                            action_implicate,
                            action_and,
                            action_or,
                            action_forall,
                            action_exists,
                            apply_exists)

from .proofs import (       action_use_proof_methods)
