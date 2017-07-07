from collections import namedtuple as nt

UnformatFile = nt('UnformatFile', 'struct result')


# NOTE: relocated unformat_file to msh.py module
def unformat_lines(lines, line_rules):
    '''Builds the LineType sequence and LineType.unformat result for a file
    line_rules: defines valid LineType succession. a dict of the form:
        parse.compile obj: (parse.compile obj, parse.compile obj, ...)
        use None for the first line
    raises TypeError if an invalid line sequence is encountered'''
    file_struct = []
    file_items = []

    for i, line in enumerate(lines):
        # skip blank lines
        if line.strip():
            try:
                PrevType = file_struct[-1]
            except IndexError:
                # first line
                PrevType = None
            for LineType in line_rules[PrevType]:
                unformat = LineType.unformat(line)
                if unformat is None:
                    # format not matched
                    continue
                else:
                    file_items.append(unformat)
                    file_struct.append(LineType)
                    break
                raise TypeError('Failed to read at '
                                'line #{:d}: {!r}'.format(i+1, line))
        else:
            file_items.append(None)
            file_struct.append(None)

    assert len(file_struct) == len(file_items)
    return UnformatFile(file_struct, file_items)
