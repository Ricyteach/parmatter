from parmatter.parmatters import BlankParmatter, FloatIntParmatter

def test_BlankParmatter():
    p = BlankParmatter('{: >5.1fblank}')
    # this next test not possible becauses parse module sprinkles stuff into regex: r'^ *(.+?)$'
    # will never match against and empty string
    # assert p.unformat('').fixed[0] == 0.0
    assert p.unformat(' ').fixed[0] == 0.0
    assert p.unformat('1.1').fixed[0] == 1.1
    assert p.format(1.1) == '  1.1'
    assert p.format(0) == '     '
    assert BlankParmatter('{:.1fblank}').format(0.0) == ' '

def test_FloatIntParmatter():
    p = FloatIntParmatter('{: >5.1fd}')
    assert p.unformat('1').fixed[0] == 1.0
    assert p.unformat('1.0').fixed[0] == 1.0
    assert p.format(1.0) == '  1.0'
    assert p.format(1) == '  1.0'

def test_BlankFloatIntParmatter():
    p = type('_', (BlankParmatter,FloatIntParmatter), {})('{: >5.1fdblank}')
    assert p.unformat('1').fixed[0] == 1.0
    assert p.unformat('1.0').fixed[0] == 1.0
    # this next test not possible becauses parse module sprinkles stuff into regex: r'^ *(.+?)$'
    # will never match against and empty string
    # assert p.unformat('').fixed[0] == 0.0
    assert p.unformat(' ').fixed[0] == 0.0
    assert p.format(1.0) == '  1.0'
    assert p.format(1) == '  1.0'
    assert p.format(0) == '     '
