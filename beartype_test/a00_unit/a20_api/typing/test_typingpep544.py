#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`544` **optimization layer unit tests.**

This submodule unit tests both the public *and* private API of the private
:mod:`beartype.typing._typingpep544` subpackage for sanity.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                             }....................
# If the active Python interpreter targets Python < 3.8 and thus fails to
# support PEP 544, skip all tests declared below.

@skip_if_python_version_less_than('3.8.0')
def test_typingpep544_metaclass() -> None:
    '''
    Test the private
    :class:`beartype.typing._typingpep544._CachingProtocolMeta` metaclass.
    '''

    # Defer heavyweight imports.
    from abc import abstractmethod
    from beartype.typing import (
        Iterable,
        Protocol,
        TypeVar,
        Union,
        runtime_checkable,
    )
    from beartype.typing._typingpep544 import _CachingProtocolMeta

    # Arbitrary type variable.
    _T_co = TypeVar('_T_co', covariant=True)

    # Can we really have it all?!
    @runtime_checkable  # <-- unnecessary at runtime, but Mypy is confused without it
    class SupportsRoundFromScratch(Protocol[_T_co]):
        __slots__: Union[str, Iterable[str]] = ()
        @abstractmethod
        def __round__(self, ndigits: int = 0) -> _T_co:
            pass

    supports_round: SupportsRoundFromScratch = 0
    assert isinstance(supports_round, SupportsRoundFromScratch)
    assert issubclass(type(SupportsRoundFromScratch), _CachingProtocolMeta)


@skip_if_python_version_less_than('3.8.0')
def test_typingpep544_protocols_typing() -> None:
    '''
    Test the public retinue of ``beartype.typing.Supports*`` protocols with
    respect to both caching optimizations implemented by the public
    :class:`beartype.typing.Protocol` subclass *and* the private
    :class:`beartype.typing._typingpep544._CachingProtocolMeta` metaclass.
    '''

    # Defer heavyweight imports.
    from decimal import Decimal
    from fractions import Fraction
    from beartype.typing import (
        SupportsAbs,
        SupportsBytes,
        SupportsComplex,
        SupportsFloat,
        SupportsIndex,
        SupportsInt,
        SupportsRound,
    )
    from beartype.typing._typingpep544 import _CachingProtocolMeta

    # Assert *ALL* standard protocols share the expected metaclass.
    for supports_t in (
        SupportsAbs,
        SupportsBytes,
        SupportsComplex,
        SupportsFloat,
        SupportsIndex,
        SupportsInt,
        SupportsRound,
    ):
        assert issubclass(type(supports_t), _CachingProtocolMeta)

    def _assert_isinstance(*types: type, target_t: type) -> None:

        assert issubclass(
            target_t.__class__, _CachingProtocolMeta
        ), (
            f'{repr(target_t.__class__)} metaclass not '
            f'{repr(_CachingProtocolMeta)}.'
        )

        for t in types:
            v = t(0)
            assert isinstance(v, target_t), (
                f'{repr(t)} not instance of {repr(target_t)}.')

    supports_abs: SupportsAbs = 0
    _assert_isinstance(
        int, float, bool, Decimal, Fraction, target_t=SupportsAbs)

    supports_complex: SupportsComplex = Fraction(0, 1)
    _assert_isinstance(
        Decimal, Fraction, target_t=SupportsComplex)

    supports_float: SupportsFloat = 0
    _assert_isinstance(
        int, float, bool, Decimal, Fraction, target_t=SupportsFloat)

    supports_int: SupportsInt = 0
    _assert_isinstance(
        int, float, bool, target_t=SupportsInt)

    supports_index: SupportsIndex = 0
    _assert_isinstance(
        int, bool, target_t=SupportsIndex)

    supports_round: SupportsRound = 0
    _assert_isinstance(
        int, float, bool, Decimal, Fraction, target_t=SupportsRound)

# ....................{ TESTS ~ custom                    }....................
@skip_if_python_version_less_than('3.8.0')
def test_typingpep544_protocols_custom_direct() -> None:
    '''
    Test the core operation of the public :class:`beartype.typing.Protocol`
    subclass with respect to user-defined :pep:`544`-compliant protocols
    directly subclassing :class:`beartype.typing.Protocol` under the
    :func:`beartype.beartype` decorator.
    '''

    # Defer heavyweight imports.
    from abc import abstractmethod
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallHintParamViolation,
        BeartypeCallHintReturnViolation,
    )
    from beartype.typing import (
        Protocol,
        Tuple,
    )
    from pytest import raises

    # Arbitrary direct protocol.
    class SupportsFish(Protocol):
        @abstractmethod
        def fish(self) -> int:
            pass

    # Arbitrary classes satisfying this protocol *WITHOUT* explicitly
    # subclassing this protocol.
    class OneFish:
        def fish(self) -> int:
            return 1

    class TwoFish:
        def fish(self) -> int:
            return 2

    # Arbitrary classes violating this protocol.
    class RedSnapper:
        def oh(self) -> str:
            return 'snap'

    # Arbitrary @beartype-decorated callable validating both parameters and
    # returns to be instances of arbitrary classes satisfying this protocol.
    @beartype
    def _real_like_identity(arg: SupportsFish) -> SupportsFish:
        return arg

    # Assert that instances of classes satisfying this protocol *WITHOUT*
    # subclassing this protocol satisfy @beartype validation as expected.
    assert isinstance(_real_like_identity(OneFish()), SupportsFish)
    assert isinstance(_real_like_identity(TwoFish()), SupportsFish)

    # Assert that instances of classes violating this protocol violate
    # @beartype validation as expected.
    with raises(BeartypeCallHintParamViolation):
        _real_like_identity(RedSnapper())  # type: ignore [arg-type]

    # Arbitrary @beartype-decorated callable guaranteed to *ALWAYS* raise a
    # violation by returning an object that *NEVER* satisfies its type hint.
    @beartype
    def _lies_all_lies(arg: SupportsFish) -> Tuple[str]:
        return (arg.fish(),)  # type: ignore [return-value]

    # Assert this callable raises the expected exception when passed an
    # instance of a class otherwise satisfying this protocol.
    with raises(BeartypeCallHintReturnViolation):
        _lies_all_lies(OneFish())


@skip_if_python_version_less_than('3.8.0')
def test_typingpep544_protocols_custom_indirect() -> None:
    '''
    Test the core operation of the public :class:`beartype.typing.Protocol`
    subclass with respect to user-defined :pep:`544`-compliant protocols
    indirectly subclassing :class:`beartype.typing.Protocol` under the
    :func:`beartype.beartype` decorator.
    '''

    # Defer heavyweight imports.
    from abc import abstractmethod
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallHintParamViolation,
        BeartypeCallHintReturnViolation,
    )
    from beartype.typing import (
        Protocol,
        Tuple,
    )
    from pytest import raises

    # Arbitrary direct protocol.
    class SupportsFish(Protocol):
        @abstractmethod
        def fish(self) -> int:
            pass

    # Arbitrary indirect protocol subclassing the above direct protocol.
    class SupportsCod(SupportsFish):
        @abstractmethod
        def dear_cod(self) -> str:
            pass

    # Arbitrary classes satisfying this protocol *WITHOUT* explicitly
    # subclassing this protocol.
    class OneCod:
        def fish(self) -> int:
            return 1

        def dear_cod(self) -> str:
            return 'Not bad, cod do better...'

    class TwoCod:
        def fish(self) -> int:
            return 2

        def dear_cod(self) -> str:
            return "I wouldn't be cod dead in that."

    # Arbitrary classes violating this protocol.
    class PacificSnapper:
        def fish(self) -> int:
            return 0xFEEDBEEF

        def dear_cod(self) -> str:
            return 'Cod you pass the butterfish?'

        def berry_punny(self) -> str:
            return 'Had a girlfriend, I lobster. But then I flounder!'

    # Arbitrary @beartype-decorated callable validating both parameters and
    # returns to be instances of arbitrary classes satisfying this protocol.
    @beartype
    def _real_like_identity(arg: SupportsCod) -> SupportsCod:
        return arg

    # Assert that instances of classes satisfying this protocol *WITHOUT*
    # subclassing this protocol satisfy @beartype validation as expected.
    assert isinstance(_real_like_identity(OneCod()), SupportsCod)
    assert isinstance(_real_like_identity(TwoCod()), SupportsCod)

    # Assert that instances of classes violating this protocol violate
    # @beartype validation as expected.
    with raises(BeartypeCallHintParamViolation):
        _real_like_identity(PacificSnapper())  # type: ignore [arg-type]

    # Arbitrary @beartype-decorated callable guaranteed to *ALWAYS* raise a
    # violation by returning an object that *NEVER* satisfies its type hint.
    @beartype
    def _lies_all_lies(arg: SupportsCod) -> Tuple[int]:
        return (arg.dear_cod(),)  # type: ignore [return-value]

    # Assert this callable raises the expected exception when passed an
    # instance of a class otherwise satisfying this protocol.
    with raises(BeartypeCallHintReturnViolation):
        _lies_all_lies(OneCod())

# ....................{ TESTS ~ pep 593                   }....................
# If the active Python interpreter targets Python < 3.9 and thus fails to
# support PEP 593, skip all PEP 593-specific tests declared below.

#FIXME: Generalize to support "typing_extensions.Annotated" as well. *sigh*
@skip_if_python_version_less_than('3.9.0')
def test_typingpep544_pep593_integration() -> None:
    '''
    Test the public :class:`beartype.typing.Protocol` subclass when nested
    within a :pep:`593`-compliant .
    '''

    # Defer heavyweight imports.
    from abc import abstractmethod
    from beartype import beartype
    from beartype.roar import BeartypeException
    from beartype.typing import (
        Annotated,
        Protocol,
    )
    from beartype.vale import Is
    from pytest import raises

    class SupportsOne(Protocol):
        @abstractmethod
        def one(self) -> int:
            pass

    class TallCoolOne:
        def one(self) -> int:
            return 1

    class FalseOne:
        def one(self) -> int:
            return 0

    class NotEvenOne:
        def two(self) -> str:
            return "two"

    @beartype
    def _there_can_be_only_one(
        n: Annotated[SupportsOne, Is[lambda x: x.one() == 1]],  # type: ignore[name-defined]
    ) -> int:
        val = n.one()
        assert val == 1  # <-- should never fail because it's caught by beartype first
        return val

    _there_can_be_only_one(TallCoolOne())

    with raises(BeartypeException):
        _there_can_be_only_one(FalseOne())

    with raises(BeartypeException):
        _there_can_be_only_one(NotEvenOne())  # type: ignore [arg-type]
