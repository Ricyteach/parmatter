from parmatter.parmatters import BlankParmatter

def test_BlankParmatter():
    b = BlankParmatter('{: >5.1fblank}')
    assert b.unformat(' ').fixed[0] == 0
    assert b.unformat(' ').fixed[0] == 0
    assert b.unformat('1.1').fixed[0] == 1.1
