from parmatter import FormatGroupMeta, FloatIntParmatter, BlankParmatter, AttrParmatter, PositionalDefaultParmatter
import pytest

s8 = '{: <8s}'
s60 = '{: <60s}'
d2 = '{: >2d}'
d3 = '{: >3d}'
d5 = '{: >5d}'


@pytest.fixture
def AComplicatedGroup():
    '''For testing the LineMaker object.'''
    class ComplicatedParmatter(BlankParmatter, FloatIntParmatter, PositionalDefaultParmatter, AttrParmatter):
        pass

    class ComplicatedGroup(metaclass=FormatGroupMeta):
        _formatter_type = ComplicatedParmatter
        _sep = ''
        _prefix = ' ' * 22 + 'A-1!!'
        Mode = (s8, 'ANALYS')
        Level = (d2, 3)
        Method = (d2, 1)
        NGroups = (d3, 1)
        Heading = (s60, 'CID from candemaker: Rick Teachey, rickteachey@cbceng.com')
        Iterations = (d5, -99)
        CulvertID = (d5, 0)
        ProcessID = (d5, 0)
        SubdomainID = (d5, 0)

    return ComplicatedGroup

def test_defaults(AComplicatedGroup):
    assert AComplicatedGroup
    s_default = AComplicatedGroup.format()
    tup1 = tuple(AComplicatedGroup.unformat(s_default))
    tup2 = tuple(v.default_namespace[0] for v in AComplicatedGroup._formatters.values())
    assert tup1 == tup2

@pytest.mark.current
@pytest.mark.parametrize("s,tup", [
    (   '                      A-1!!ANALYS   3 1  1ABC                                                        -99    0    0    0',
        ('ANALYS', 3, 1, 1, 'ABC', -99, 0, 0, 0)
    ),
    (   '                      A-1!!ANALYS   3 1  1123                                                        -99    0    0    0',
        ('ANALYS', 3, 1, 1, '123', -99, 0, 0, 0)
    ),
    ])
def test_some_tricky_ones(AComplicatedGroup, s, tup):
    s_tup = tuple(AComplicatedGroup.unformat(s))
    assert s_tup == tup
