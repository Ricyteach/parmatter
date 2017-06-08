from parmatter import FormatGroup as LineMaker
import pytest
from collections import namedtuple as nt

def test_LineMaker():
    assert LineMaker('EmptyLineDef')
    
def test_basic_LineMaker():
    assert LineMaker('BasicLineDef', a='{: >5s}')
    
@pytest.fixture
def ALineDefClass():
    '''For testing the LineMaker object.'''
    ALineDef = LineMaker('ALineDef', a = '{: >5d}', b = ('{: >10f}', 0), c = ('{: >2s}', ''), d = '{}')
    return ALineDef
    
@pytest.fixture()
def ALineDefMembers(ALineDefClass, scope='function'):
    '''For testing the LineMaker object.'''
    return list(ALineDefClass)
    
@pytest.fixture()
def ABCD_namedtuple(scope='function'):
    '''Helper tuple for testing ALineDefClass'''
    ABCD = nt('ABC', 'a b c d')
    return ABCD
    
def test_init(ALineDefClass):
    a,b,c,d=ALineDefClass
    assert a._format_str == '{: >5d}'
    assert b._format_str == '{: >10f}'
    assert c._format_str == '{: >2s}'
    assert d._format_str == '{}'
    assert ALineDefClass._prefix == ''
    assert ALineDefClass._sep == ''
    
def test_member_format(ALineDefMembers):
    a,b,c,d = ALineDefMembers
    assert a.format(1) == '    1'
    with pytest.raises(IndexError):
        a.format()
    with pytest.raises(ValueError):
        a.format('')
    assert b.format(3) == '  3.000000'
    assert b.format() == '  0.000000'
    assert c.format('c') == ' c'
    assert c.format() == '  '
    assert d.format(3) == '3'
    with pytest.raises(IndexError):
        d.format()
        
def test_class_format_tuple(ALineDefClass, ALineDefMembers, ABCD_namedtuple):
    a,b,c,d = ALineDefMembers
    abcd = ABCD_namedtuple(1,2,'x','foo')
    assert ALineDefClass.format(abcd) == '    1  2.000000 xfoo'
    
def test_class_format_dict(ALineDefClass, ALineDefMembers):
    assert ALineDefClass.format(dict(a=1, d='d')) == '    1  0.000000  d'
    with pytest.raises(IndexError):
        ALineDefClass.format(dict(a=1))

def test_class_format_mixture(ALineDefClass, ALineDefMembers, ABCD_namedtuple):
    a,b,c,d = ALineDefMembers
    a_nt = nt('A', 'a')(1)
    assert ALineDefClass.format(a_nt, dict(d='d')) == '    1  0.000000  d'
    with pytest.raises(IndexError):
        ALineDefClass.format(a_nt, dict(b=3))
    assert ALineDefClass.format(a_nt, dict(c = 'xx', d='bar')) == '    1  0.000000xxbar'
    
def test_class_format_name_conflicts(ALineDefClass, ALineDefMembers, ABCD_namedtuple):
    abcd = ABCD_namedtuple(1,2,3,4)
    with pytest.raises(ValueError):
        ALineDefClass.format(abcd, dict(b=331))
    with pytest.raises(ValueError):
        ALineDefClass.format(abcd, **dict(b=331))
        
@pytest.mark.skip(reason="haven't decided whether/how to disallow overflow of width for fields")
def test_class_format_field_overflow(ALineDefClass, ALineDefMembers, ABCD_namedtuple):
    with pytest.raises(ValueError):
        ALineDefClass.format(dict(a=123456, d='d'))

def test_LineMakerFactory_basic():
    LineDef = LineMaker('LineDef', a = '{}')
    assert LineDef.format(dict(a=1)) == '1'
    assert LineDef.format(dict(a='string')) == 'string'
    
def test_LineMakerFactory_prefix():
    LineDef = LineMaker('LineDef', a = '{}', b = '{: >5d}', c = '{}', prefix = '          LALALA')
    assert LineDef.format(dict(a=1, b=1, c='')) == '          LALALA1    1'
    
def test_LineMakerMeta_prefix_set():
    LineDef = LineMaker('LineDef', a = '{}', b = '{: >5d}', c = ('{}',''), prefix = '          LALALA')
    LineDef._prefix = ''
    assert LineDef.format(dict(a=1, b=1)) == '1    1'
    
#NOTE: the parse module seems to have some trouble with string fields and spaces around them. don't implicitly trust it. 
@pytest.mark.parametrize('string, format_string, values',[
                    ('    3    -3.012 4 5', '{: >5d}{: >10f}{: >2d}{: >2d}', (3, float(-3.012), 4, 5)),
                    ('    3    -3.012 4 5', '{: >5d}{: >10f}{: >2d}{: >2d}', (3, float(-3.012), 4, 5)),
                    ])
def test_LineDefClass_unformat(string, format_string, values):
    ALineDefClass = LineMaker('ALineDefClass', a = '{: >5d}', b = ('{: >10f}', 0), c = ('{: >2d}', ''), d = '{: >2d}')
    assert format_string == ALineDefClass._prefix+ALineDefClass._sep.join(member._format_str for member in ALineDefClass)
    test = tuple(ALineDefClass.unformat(string))
    assert test == values

@pytest.mark.parametrize('cls, format_string, string, values',[
                    (LineMaker('cls', a = '{: >5d}', b = ('{: >10f}', 0), c = ('{: >2d}', ''), sep = ','), '{: >5d},{: >10f},{: >2d}', '    3,    -3.012, 4', (3, float(-3.012), 4)),
                    (LineMaker('cls', a = '{: >5d}', b = ('{: >10f}', 0), c = ('{: >2s}', ''), sep = ','), '{: >5d},{: >10f},{: >2s}', '    3,    -3.012, foo', (3, float(-3.012), 'foo')),
                    ])
def test_LineDefClass_unformat_with_sep(cls, format_string, string, values):
    assert format_string == cls._prefix+cls._sep.join(member._format_str for member in cls)
    test = tuple(cls.unformat(string))
    assert test == values