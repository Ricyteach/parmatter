from parmatter.utilities import set_item_if, update_special, slice_to_range, args_kwargs_from_args
from collections import namedtuple as nt
import pytest

@pytest.fixture
def ABCD_namedtuple(scope='function'):
    '''Helper tuple for testing ALineDefClass'''
    ABCD = nt('ABCD', 'a b c d')
    return ABCD
    
@pytest.fixture
def obj(scope='function'):
    return 'abcdefg'

@pytest.mark.parametrize("test_input, expected", [
    (slice(10), range(10)),
    (slice(None), range(len('abcdefg'))),
    (slice(-1,7), range(-1,7)),
    (slice(-1,7,-1), range(-1,7,-1)),
    (slice(1,-2,-1), range(1,-2,-1)),
    (slice(None,-2,-1), range(-1,-2,-1)),
    (slice(None,-2), range(-1,-2)),
    (slice(-3), range(0,-3)),
])
def test_slice_to_range(test_input, expected, obj):
    rng = slice_to_range(test_input, obj)
    assert rng==expected
    for i,o in zip(rng, obj[test_input]):
        assert obj[i] == o

def test_args_kwargs_from_args(ABCD_namedtuple):
    abcd = ABCD_namedtuple(1,2,'x','foo')
    args_i = 1, dict(a=1, b=2), 2, 3, dict(c=3, b=4), abcd
    slc=slice(-1,None,-1)
    asdict=True
    ignore_conflicts=True
    terminate_on_failure=True
    args_f, kwargs = args_kwargs_from_args(args_i, slc=slc, asdict=asdict, ignore_conflicts=ignore_conflicts, terminate_on_failure=terminate_on_failure)
    assert args_f == [1,dict(a=1, b=2),2,3]