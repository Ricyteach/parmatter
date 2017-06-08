parmatter
=========

Tools for formatters that can also parse strings (i.e., with `unformat()` capability): a.k.a., "parmatters". 

The `unformat` methods return `parse.Result` instances from the parse project. 

Basic parmatter
---------------

Example usage: 

    >>> f = Parmatter()
    >>> assert f.format('{x}', x='foo') == 'foo'
    >>> assert f.format('{}', 'foo') == 'foo'
    >>> assert list(f.unformat('{}', 'foo')) == ['foo']
    
Custom parmatters
-----------------
    
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
*  `format` method can populate fields using attributes from an object provided as an argument

        >>> obj = type('MyClass', (), {})()
        >>> obj.x = 'foo'
        >>> f = VersatileParmatter('{x}: {}', 'bar')
        >>> assert f.format(obj) == 'foo: bar'
        >>> f.unformat('foo: bar')
        <Result ('foo',) {'x': 'bar'}>

Basic Format Groups
-------------------

Parmatter groups are created in order to define different line types for files. 

An individual parmatter could also define a line type on its own, but the parmatter group also has options for prefixes, separators, and naming of parmatters (useful in formatting and unformatting). The basic `FormatGroup` factory uses the `VersatileParmatter` by default. Note that the `parse.Result` object has been modified to make use of a named tuples; the named tuple fields are named for the `FormatGroup` arguments.

Example usage:

    >>> NodeCount = FormatGroup('NodeCount', Total = '{: >5d}')
    >>> NodeCount.unformat('    10').fixed
    NodeCountData(Total=10)
    >>> NodeCount.format(10)
    '   10'
    >>> NodeLine = FormatGroup('NodeLine', Num = '{: >5d}', X = ('{: >10f}', 0), Y = ('{: >10f}', 0))
    >>> NodeLine.unformat('    1    0.0000    0.0000').fixed
    NodeLineData(Num=1, X=0.0, Y=0.0)
    >>> NodeLine.format(1,5,6.3)
    '    5    5.0000    6.3000'

File Unformat
-------------------

Builds the LineType sequence and LineType.unformat result for a file. Raises TypeError if an invalid line sequence is encountered.

Use `line_rules` to define valid LineType succession (i.e., which line types are allowed to follow a given line type). Use `None` for the first line. 

Given some example file (representing a group of 4 nodes) at 'SOME_PATH' and the `NodeCount`, `NodeLine` format groups above:

        4
        1       0.0       0.0
        2       1.0       0.0
        3       0.0       1.0
        4       1.0       1.0

Unformat the file thusly:
    
    >>> line_rules={    None:(NodeCount),
                        NodeCount:(NodeLine),
                        NodeLine:(NodeLine),
                        }
    >>> from pathlib import Path
    >>> path = Path('SOME_PATH')
    >>> unformat_tuple = unformat_file(path, line_rules)
    UnformatFile = nt('UnformatFile', 'unformat_tuple.result')
    >>> unformat_tuple.struct
    [NodeCount, NodeLine, NodeLine, NodeLine, NodeLine]
    >>> unformat_tuple.result
    [<Result (4) {}>, <Result (1, 0.0, 0.0) {}>, <Result (2, 1.0, 0.0) {}>, <Result (3, 0.0, 1.0) {}>, <Result (4, 1.0, 1.0) {}>]
    
Make use of the file data:
    
    >>> node4 = unformat_tuple.result[-1].fixed
    >>> node4
    NodeLineData(Num=4, X=1.0, Y=1.0)
    >>> node4._asdict()
    OrderedDict([('Num', 4), ('X', 1.0), ('Y', 1.0)])
    >>> NodeLine.format(node4)
    '    4       1.0       1.0'