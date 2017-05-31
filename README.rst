parmatter
--------

Tools for parsable formatters (with unformat() capability).

Example usage: 

    >>> f = Parmatter()
    >>> assert f.format('{}', 'foo') = 'foo'
    >>> assert list(f.unformat('{}', 'foo')) = ['foo']
