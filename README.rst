parmatter
--------

Tools for parsing formatters (that can also parse strings, i.e., with unformat() capability).

Example usage: 

    >>> f = Parmatter()
    >>> assert f.format('{}', 'foo') = 'foo'
    >>> assert list(f.unformat('{}', 'foo')) = ['foo']
