#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator **wrapper function code snippets** (i.e., triple-quoted
pure-Python string constants formatted and concatenated together to dynamically
generate the implementations of wrapper functions type-checking
:func:`beartype.beartype`-decorated callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.checkmagic import (
    VAR_NAME_PITH_ROOT,
    VAR_NAME_RANDOM_INT,
)
from beartype._check.checkmagic import (
    ARG_NAME_BEARTYPE_CONF,
    ARG_NAME_FUNC,
    ARG_NAME_RAISE_EXCEPTION,
    VAR_NAME_ARGS_LEN,
)
from beartype._data.datakind import ARG_NAME_RETURN_REPR
from beartype._util.func.arg.utilfuncargiter import ArgKind
from beartype._util.text.utiltextmagic import CODE_INDENT_1

# ....................{ CODE                               }....................
CODE_SIGNATURE = f'''{{code_signature_prefix}}def {{func_name}}(
    *args,
{{code_signature_args}}{CODE_INDENT_1}**kwargs
):'''
'''
Code snippet declaring the signature of a type-checking callable.

Note that:

* ``code_signature_prefix`` is usually either:

  * For synchronous callables, the empty string.
  * For asynchronous callables (e.g., asynchronous generators, coroutines),
    the space-suffixed keyword ``"async "``.
'''


CODE_INIT_ARGS_LEN = f'''
    # Localize the number of passed positional arguments for efficiency.
    {VAR_NAME_ARGS_LEN} = len(args)'''
'''
PEP-agnostic code snippet localizing the number of passed positional arguments
for callables accepting one or more such arguments.
'''

# ....................{ CODE ~ check                       }....................
CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER = '?|PITH_ROOT_NAME`^'
'''
Placeholder source substring to be globally replaced by the **root pith name**
(i.e., name of the current parameter if called by the
:func:`pep_code_check_param` function *or* ``return`` if called by the
:func:`pep_code_check_return` function) in the parameter- and return-agnostic
code generated by the memoized :func:`make_func_wrapper_code` function.

See Also
----------
:func:`beartype._check.expr.exprmake.make_func_wrapper_code`
:attr:`beartype._util.error.utilerror.EXCEPTION_PLACEHOLDER`
    Related commentary.
'''


CODE_HINT_ROOT_PREFIX = '''
        # Type-check this passed parameter or return value against this
        # PEP-compliant type hint.
        if not '''
'''
PEP-compliant code snippet prefixing all code type-checking the **root pith**
(i.e., value of the current parameter or return value) against the root
PEP-compliant type hint annotating that pith.

This prefix is intended to be locally suffixed in the
:func:`beartype._check.expr.exprmake.make_func_wrapper_code` function by:

#. The value of the ``hint_child_placeholder`` local variable.
#. The :data:`CODE_HINT_ROOT_SUFFIX` suffix.
'''


CODE_HINT_ROOT_SUFFIX = f''':
            raise {ARG_NAME_RAISE_EXCEPTION}(
                func={ARG_NAME_FUNC},
                conf={ARG_NAME_BEARTYPE_CONF},
                pith_name={CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER},
                pith_value={VAR_NAME_PITH_ROOT},{{random_int_if_any}}
            )
'''
'''
PEP-compliant code snippet suffixing all code type-checking the **root pith**
(i.e., value of the current parameter or return value) against the root
PEP-compliant type hint annotating that pith.

This snippet expects to be formatted with these named interpolations:

* ``{random_int_if_any}``, whose value is either:

  * If type-checking the current type hint requires a pseudo-random integer,
    :data:`CODE_HINT_ROOT_SUFFIX_RANDOM_INT`.
  * Else, the empty substring.

Design
----------
**This string is the only code snippet defined by this submodule to raise an
exception.** All other such snippets only test the current pith against the
current child PEP-compliant type hint and are thus intended to be dynamically
embedded in the conditional test initiated by the
:data:`CODE_HINT_ROOT_PREFIX` code snippet.
'''


CODE_HINT_ROOT_SUFFIX_RANDOM_INT = f'''
                random_int={VAR_NAME_RANDOM_INT},'''
'''
PEP-compliant code snippet passing the value of the random integer previously
generated for the current call to the exception-handling function call embedded
in the :data:`CODE_HINT_ROOT_SUFFIX` snippet.
'''

# ....................{ CODE ~ arg                         }....................
PARAM_KIND_TO_CODE_LOCALIZE = {
    # Snippet localizing any positional-only parameter (e.g.,
    # "{posonlyarg}, /") by lookup in the wrapper's "*args" dictionary.
    ArgKind.POSITIONAL_ONLY: f'''
    # If this positional-only parameter was passed...
    if {VAR_NAME_ARGS_LEN} > {{arg_index}}:
        # Localize this positional-only parameter.
        {VAR_NAME_PITH_ROOT} = args[{{arg_index}}]''',

    # Snippet localizing any positional or keyword parameter as follows:
    #
    # * If this parameter's 0-based index (in the parameter list of the
    #   decorated callable's signature) does *NOT* exceed the number of
    #   positional parameters passed to the wrapper function, localize this
    #   positional parameter from the wrapper's variadic "*args" tuple.
    # * Else if this parameter's name is in the dictionary of keyword
    #   parameters passed to the wrapper function, localize this keyword
    #   parameter from the wrapper's variadic "*kwargs" tuple.
    # * Else, this parameter is unpassed. In this case, localize this parameter
    #   as a placeholder value guaranteed to *NEVER* be passed to any wrapper
    #   function: the private "__beartypistry" singleton passed to this wrapper
    #   function as a hidden default parameter and thus accessible here. While
    #   we could pass a "__beartype_sentinel" parameter to all wrapper
    #   functions defaulting to "object()" and then use that here instead,
    #   doing so would slightly reduce efficiency for no tangible gain. *shrug*
    ArgKind.POSITIONAL_OR_KEYWORD: f'''
    # Localize this positional or keyword parameter if passed *OR* to the
    # sentinel "__beartype_raise_exception" guaranteed to never be passed.
    {VAR_NAME_PITH_ROOT} = (
        args[{{arg_index}}] if {VAR_NAME_ARGS_LEN} > {{arg_index}} else
        kwargs.get({{arg_name!r}}, {ARG_NAME_RAISE_EXCEPTION})
    )

    # If this parameter was passed...
    if {VAR_NAME_PITH_ROOT} is not {ARG_NAME_RAISE_EXCEPTION}:''',

    # Snippet localizing any keyword-only parameter (e.g., "*, {kwarg}") by
    # lookup in the wrapper's variadic "**kwargs" dictionary. (See above.)
    ArgKind.KEYWORD_ONLY: f'''
    # Localize this keyword-only parameter if passed *OR* to the sentinel value
    # "__beartype_raise_exception" guaranteed to never be passed.
    {VAR_NAME_PITH_ROOT} = kwargs.get({{arg_name!r}}, {ARG_NAME_RAISE_EXCEPTION})

    # If this parameter was passed...
    if {VAR_NAME_PITH_ROOT} is not {ARG_NAME_RAISE_EXCEPTION}:''',

    # Snippet iteratively localizing all variadic positional parameters.
    ArgKind.VAR_POSITIONAL: f'''
    # For all passed variadic positional parameters...
    for {VAR_NAME_PITH_ROOT} in args[{{arg_index!r}}:]:''',

    #FIXME: Probably impossible to implement under the standard decorator
    #paradigm, sadly. This will have to wait for us to fundamentally revise
    #our signature generation algorithm.
    # # Snippet iteratively localizing all variadic keyword parameters.
    # ArgKind.VAR_KEYWORD: f'''
    # # For all passed variadic keyword parameters...
    # for {VAR_NAME_PITH_ROOT} in kwargs[{{arg_index!r}}:]:''',
}
'''
Dictionary mapping from the type of each callable parameter supported by the
:func:`beartype.beartype` decorator to a PEP-compliant code snippet localizing
that callable's next parameter to be type-checked.
'''

# ....................{ CODE ~ return ~ check              }....................
CODE_RETURN_CHECK_PREFIX = f'''
    # Call this function with all passed parameters and localize the value
    # returned from this call.
    {VAR_NAME_PITH_ROOT} = {{func_call_prefix}}{ARG_NAME_FUNC}(*args, **kwargs)

    # Noop required to artificially increase indentation level. Note that
    # CPython implicitly optimizes this conditional away. Isn't that nice?
    if True:'''
'''
PEP-compliant code snippet calling the decorated callable and localizing the
value returned by that call.

Note that this snippet intentionally terminates on a noop increasing the
indentation level, enabling subsequent type-checking code to effectively ignore
indentation level and thus uniformly operate on both:

* Parameters localized via values of the
  :data:`PARAM_KIND_TO_PEP_CODE_LOCALIZE` dictionary.
* Return values localized via this snippet.

See Also
----------
https://stackoverflow.com/a/18124151/2809027
    Bytecode disassembly demonstrating that CPython optimizes away the spurious
   ``if True:`` conditional hardcoded into this snippet.
'''


CODE_RETURN_CHECK_SUFFIX = f'''
    return {VAR_NAME_PITH_ROOT}'''
'''
PEP-compliant code snippet returning from the wrapper function the successfully
type-checked value returned from the decorated callable.
'''

# ....................{ CODE ~ return ~ check ~ noreturn   }....................
#FIXME: *FALSE.* The following comment is entirely wrong, sadly. Although that
#comment does, in fact, apply to asynchronous generators, that comment does
#*NOT* apply to coroutines. PEP 484 stipulates that the returns of coroutines
#are annotated in the exact same standard way as the returns of synchronous
#callables are annotated: e.g.,
#   # This is valid, but @beartype currently fails to support this.
#   async def muh_coroutine() -> typing.NoReturn:
#       await asyncio.sleep(0)
#       raise ValueError('Dude, who stole my standards compliance?')
#
#Generalize this snippet to contain a "{{func_call_prefix}}" substring prefixing
#the "{ARG_NAME_FUNC}(*args, **kwargs)" call, please.

# Unlike above, this snippet intentionally omits the "{{func_call_prefix}}"
# substring prefixing the "{ARG_NAME_FUNC}(*args, **kwargs)" call. Why? Because
# callables whose returns are annotated by "typing.NoReturn" *MUST* necessarily
# be synchronous (rather than asynchronous) and thus require no such prefix.
# Why? Because the returns of asynchronous callables are either unannotated
# *OR* annotated by either "Coroutine[...]" *OR* "AsyncGenerator[...]" type
# hints. Since "typing.NoReturn" is neither, "typing.NoReturn" *CANNOT*
# annotate the returns of asynchronous callables. The implication then follows.
PEP484_CODE_CHECK_NORETURN = f'''
    # Call this function with all passed parameters and localize the value
    # returned from this call.
    {VAR_NAME_PITH_ROOT} = {{func_call_prefix}}{ARG_NAME_FUNC}(*args, **kwargs)

    # Since this function annotated by "typing.NoReturn" successfully returned a
    # value rather than raising an exception or halting the active Python
    # interpreter, unconditionally raise an exception.
    raise {ARG_NAME_RAISE_EXCEPTION}(
        func={ARG_NAME_FUNC},
        conf={ARG_NAME_BEARTYPE_CONF},
        pith_name={ARG_NAME_RETURN_REPR},
        pith_value={VAR_NAME_PITH_ROOT},
    )'''
'''
:pep:`484`-compliant code snippet calling the decorated callable annotated by
the :attr:`typing.NoReturn` singleton and raising an exception if this call
successfully returned a value rather than raising an exception or halting the
active Python interpreter.
'''

# ....................{ CODE ~ return ~ uncheck            }....................
CODE_RETURN_UNCHECKED = f'''
    # Call this function with all passed parameters and return the value
    # returned from this call.
    return {{func_call_prefix}}{ARG_NAME_FUNC}(*args, **kwargs)'''
'''
PEP-agnostic code snippet calling the decorated callable *without*
type-checking the value returned by that call (if any).
'''
