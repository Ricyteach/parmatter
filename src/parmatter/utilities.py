from collections import OrderedDict as od

def set_item_if(obj, name, value, test):
    '''Sets an item of obj to a value if test passes.
    The test signature must be of the form:
        test(obj,name,value)'''
    # allow for individual arguments or iterables
    try:
        names = [name] if isinstance(name, str) else (*name,)
    except TypeError:
        names = [name]
    try:
        values = [value] if isinstance(value, str) else (*value,)
    except TypeError:
        values = [value]
    # check that same number of names and values provided
    if len(names)!=len(values):
        raise ValueError('Unequal number of names ({}) and values ({}) provided.'.format(len(names), len(values)))
    # set items based on test result
    for name,value in zip(names, values):
        if test(obj,name,value):
            obj[name] = value

def update_special(d, **kwargs):
    '''Update a dict as usual, but an error is raised if there are duplicate keys.'''
    try:
        conflict = next(k for k in kwargs if k in d)
    except StopIteration:
        d.update(**kwargs)
    else:
        raise ValueError('Duplicate key detected: "{}".'.format(conflict))
        
def slice_to_range(slc, obj=None):
    '''Creates a range composed of the indexes of a slice for a collection object.
    Note that the range DOES continue past zero; however slices do not do this.
    To track indexes of slices, do:
        for i,v in zip(slice_to_range(slc, obj), obj[slc]):'''
    step = slc.step if slc.step is not None else 1
    start = slc.start if slc.start is not None else -1 if step<0 else 0
    stop = slc.stop if slc.stop is not None else -(len(obj)+1) if step<0 else len(obj)
    return range(start,stop,step)
        
def args_kwargs_from_args(args, slc=slice(0,None), asdict=True, ignore_conflicts=True, terminate_on_failure=True):
    '''Given an args list and slice, remove any kwarg-like objects from the list,
    including objects with asdict or _asdict methods, and return in a separate namespace.
    The order of resulting args or kwargs is not affected.'''
    # maintain order since intended to be used as a function namespace
    kwargs = od()
    if isinstance(args, str):
        return [args], kwargs
    args = args[:]
    rng = slice_to_range(slc, args)
    remove_i = []
    if ignore_conflicts:
        update = od.update
    else:
        update = update_special
    for i,arg in zip(rng, args[slc]):
        try:
            try:
                d = od(**arg)
            except TypeError:
                if asdict:
                    try:
                        conversion = arg.asdict
                    except AttributeError:
                        conversion = arg._asdict
                    try:
                        d = od(**conversion())
                    except TypeError:
                        d = od(**conversion)
                else:
                    raise
        except (AttributeError, TypeError):
            if terminate_on_failure:
                break
            else:
                continue
        else:
            update(kwargs, **d)
            remove_i.append(i)
    # adjust in the case  that the slice was reverse order
    remove_i = [i+len(args) if i<0 else i for i in remove_i]
    args = [args[i] for i in range(len(args)) if i not in remove_i]
    return args, kwargs

def auto_save_as(filepath, saveaspath = None, ext = None):
    '''Provides a path-like object for saving a filepath under a new path.
    
    Will use the provided ext for the new file extension.
    If no saveaspath is provided, the same input file name is used; the input file extension
    will also be used if one is not provided. 
    If saveaspath is provided with no extension, the saveaspath is assumed to be directory.'''
    
    if saveaspath is None:
        savedir = filepath.parent
        savename = filepath.stem
        if ext is None:
            ext = filepath.suffix
    else:
        if saveaspath.suffix == '':
            savedir = saveaspath
            savename = filepath.stem
            ext = saveaspath.suffix
        else:
            savedir = saveaspath.parent
            savename = saveaspath.stem
            if ext != saveaspath.suffix:
                raise ValueError('Cannot resolve conflicting save as extensions.')

    savefile = type(saveaspath)(savename).with_suffix(ext)
    return savedir/savefile
    
