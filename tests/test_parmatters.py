from parmatter import StaticParmatter, DefaultParmatter, AttrParmatter, PositionalDefaultParmatter, KeywordParmatter, VersatileParmatter
import pytest

def test_StaticParmatter():
    f=StaticParmatter('{: >5d}')
    assert f.format(1) == '    1'
    with pytest.raises(IndexError):
        f.format()
    with pytest.raises(ValueError):
        f.format('')
    f=StaticParmatter('{a: >5d}')
    with pytest.raises(KeyError):
        f.format()
    with pytest.raises(ValueError):
        f.format(a='')
    
def test_DefaultParmatter():
    f=DefaultParmatter({0: 1})
    assert f.format('{: >5d}') == '    1'
    with pytest.raises(IndexError):
        f.format('{: >5d}{: >5d}')
    with pytest.raises(ValueError):
        f.format('{: >5s}')
    f=DefaultParmatter(dict(a=1,b=2,c=3))
    assert f.format('{a: >5d}{b: >5d}') == '    1    2'
    with pytest.raises(KeyError) as exc:
        f.format('{a: >5d}{d: >5d}')
    assert "key = 'd'" in str(exc.value)
    with pytest.raises(ValueError) as exc:
        f.format('{a: >5s}')
    assert "format code 's'" in str(exc.value)
        
def test_AttrParmatter():
    f=AttrParmatter()
    assert f.format('{a: >5d}', a=1) == '    1'
    class C(): pass
    c=C()
    setattr(c,'a',1)
    assert f.format('{a: >5d}', c) == '    1'
    with pytest.raises(ValueError):
        f.format('{a: >5d}', c, a=1) == '    1'
    assert f.format('{a: >5d}{b: >5d}', c, b=2) == '    1    2'
    
def test_PositionalDefaultParmatter():
    f=PositionalDefaultParmatter(1,2,3)
    assert f.format('{: >5d}{: >5d}') == '    1    2'
    with pytest.raises(KeyError):
        f.format('{: >5d}{b: >5d}') == '    1    2'
        
def test_KeywordParmatter():
    f=KeywordParmatter('{a: >5d}{b: >5d}', dict(a=1,b=2,c=3))
    assert f.format() == '    1    2'
    
def test_VersatileParmatter():
    f=VersatileParmatter('{: >5d}{: >5d}', 1,2,3)
    assert f.format() == '    1    2'
    f=VersatileParmatter('{: >5d}{: >5d}{: >5d}', 1,2,3)
    assert f.format() == '    1    2    3'
    f=VersatileParmatter('{: >5d}{: >5d}{a: >5d}{: >5d}', 1,2,3, default_namespace=dict(a=4))
    assert f.format() == '    1    2    4    3'
    f=VersatileParmatter('{: >5d}{: >5d}{a: >5d}{: >5d}')
    with pytest.raises((IndexError, KeyError)) as exc:
        f.format()
    with pytest.raises(ValueError):
        f.format('{: >5s}')
        
def test_StaticParmatter_parse():
    f=StaticParmatter('{: >5d}')
    assert f.format(1) == '    1'
    assert list(f.unformat('    1')) == [1]

@pytest.mark.parametrize('format, string, values',[
                    ('{: >5d}{: >10.3f}{: >2s}', '    3    -3.012 x', (3, float(-3.012), 'x')),
                    ('{: >5d}{: >10.3f}{: >2s}{: >4s}', '    3    -3.012 xlala', (3, float(-3.012), 'x', 'lala')),
                    ])
def test_VersatileParmatter_parse(format, string, values):
    f=VersatileParmatter(format)
    test = f.unformat(string)
    assert tuple(test) == values