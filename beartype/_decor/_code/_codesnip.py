#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator general-purpose code snippets.**

This private submodule *only* defines **code snippets** (i.e., triple-quoted
pure-Python code constants formatted and concatenated together into wrapper
functions implementing type-checking for decorated callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ CONSTANTS ~ param                 }....................
PARAM_NAME_FUNC = '__beartype_func'
'''
Name of the **private decorated callable parameter** (i.e.,
:mod:`beartype`-specific parameter whose default value is the decorated
callable implicitly passed to all wrapper functions generated by the
:func:`beartype.beartype` decorator).
'''


PARAM_NAME_TYPISTRY = '__beartypistry'
'''
Name of the **private beartypistry parameter** (i.e., :mod:`beartype`-specific
parameter whose default value is the beartypistry singleton implicitly passed
to all wrapper functions generated by the :func:`beartype.beartype` decorator).
'''

# ....................{ CODE                              }....................
CODE_SIGNATURE = '''def {{func_wrapper_name}}(
    *args,
    {param_name_func}={param_name_func},
    {param_name_typistry}={param_name_typistry},
    **kwargs
):'''.format(
    param_name_func=PARAM_NAME_FUNC,
    param_name_typistry=PARAM_NAME_TYPISTRY,
)
'''
PEP-agnostic code snippet declaring the signature of the wrapper function
type-checking the decorated callable.
'''


CODE_RETURN_UNCHECKED = '''
    # Call this function with all passed parameters and return the value
    # returned from this call.
    return {param_name_func}(*args, **kwargs)'''.format(
        param_name_func=PARAM_NAME_FUNC)
'''
PEP-agnostic code snippet calling the decorated callable *without*
type-checking the value returned by that call (if any).
'''

# ....................{ CODE ~ param                      }....................
CODE_PARAMS_POSITIONAL_INIT = '''
    # Localize the number of passed positional arguments for efficiency.
    __beartype_args_len = len(args)'''
'''
PEP-agnostic code snippet localizing the number of passed positional arguments
for callables accepting one or more such arguments.
'''

# ....................{ CODE ~ indent                     }....................
CODE_INDENT_1 = '    '
'''
PEP-agnostic code snippet expanding to a single level of indentation.
'''


CODE_INDENT_2 = CODE_INDENT_1*2
'''
PEP-agnostic code snippet expanding to two levels of indentation.
'''


CODE_INDENT_3 = CODE_INDENT_2 + CODE_INDENT_1
'''
PEP-agnostic code snippet expanding to three levels of indentation.
'''
