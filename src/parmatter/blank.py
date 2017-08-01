from .minilang import parse_spec

class BlankBase():
    '''An object that prints as blank if it is falsey. Also supports
    a new format spec: "blank" at the end of any other spec.'''
    def __str__(self):
        return '' if not self else super().__str__()
    def __repr__(self):
        return '{}({})'.format(type(self).__name__, super().__repr__())
    def __format__(self, spec):
        spec_tup = parse_spec(spec, strict=False)
        # always remove "blank" from spec type
        spec = spec_tup._replace(type=spec_tup.type.replace('blank', '')).join()
        # only act on "blank"  if object is falsey
        if 'blank' in spec_tup.type and not self:
            spec = spec_tup._replace(type='s').join()
            result = format('', spec)
        else:
            result = super().__format__(spec)
        return result


class BlankInt(BlankBase, int):
    '''An int that prints blank when zero.'''
    pass


class BlankFloat(BlankBase, float):
    '''A float that prints blank when zero.'''
    pass

def make_blank(value, cls=None):
    if cls is None:
        cls = type(value)
    new_cls = type('Blank_{}'.format(cls.__name__), (BlankBase, cls), {})
    return new_cls(value)
