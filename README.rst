parmatter
--------

Tools for formatters that can also parse strings (i.e., with `unformat()` capability): a.k.a., "parmatters". 

The `unformat` methods return `parse.Result` instances from the `parse <https://pypi.python.org/pypi/parse>` module. 

Example usage: 

    >>> f = Parmatter()
    >>> assert f.format('{x}', x='foo') == 'foo'
    >>> assert f.format('{}', 'foo') == 'foo'
    >>> assert list(f.unformat('{}', 'foo')) == ['foo']
    
Some custom parmatters are also available. 

`StaticParmatter` is a parmatter with a pre-compiled (i.e., static) parser:

    >>> f = StaticParmatter('{}')
    >>> assert f.format('foo') == 'foo'
    >>> assert list(f.unformat('foo')) == ['foo']
    
`DefaultParmatter` is a parmatter with a default namespace. The namespace should have `int` keys for positional arguments, and `str` keys for named arguments:

    >>> f = DefaultParmatter(default_namespace={0:'foo', 'a':'bar'})
    >>> assert f.format('{}: {a}') == 'foo: bar'
    >>> f.unformat('{}: {a}','foo: bar')
    <Result ('foo',) {'a': 'bar'}>

`PositionalDefaultParmatter` is a parmatter with a default *positional* namespace:

    >>> f = PositionalDefaultParmatter('foo', 'bar')
    >>> assert f.format('{}: {}') == 'foo: bar'
    >>> assert f.format('{}: {}', 'baz') == 'baz: bar'
    >>> assert list(f.unformat('{}: {}', 'foo: bar')) == ['foo', 'bar']
    
`KeywordParmatter` is a parmatter with a default *keyword* namespace:

    >>> f = KeywordParmatter(x='foo', y='bar')
    >>> assert f.format('{x}: {y}') == 'foo: bar'
    >>> assert f.format('{x}: {y}', y='baz') == 'foo: baz'
    >>> f.unformat('{x}: {y}', 'foo: bar')
    <Result () {'x': 'foo', 'y': 'bar'}>
    
`AttrParmatter` is a parmatter whose `format` method can populate fields using attributes from an object provided as an argument: 

    >>> obj = type('MyClass', (), {})()
    >>> obj.x = 'foo'
    >>> f = AttrParmatter()
    >>> assert f.format('{x}', obj) == 'foo'
    >>> f.unformat('{x}', 'foo')
    <Result () {'x': 'foo'}>
    
`VersatileParmatter` is a parmatter with a combination of the above functionalities:
*  a pre-compiled (i.e., static) parser
*  a default *positional* namespace
*  `format` method can populate fields using attributes from an object provided as an argument: 

    >>> obj = type('MyClass', (), {})()
    >>> obj.x = 'foo'
    >>> f = VersatileParmatter('{x}: {}', 'bar')
    >>> assert f.format(obj) == 'foo: bar'
    >>> f.unformat('foo: bar')
    <Result ('foo',) {'x': 'bar'}>
