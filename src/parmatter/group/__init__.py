'''Parmatter groups are created in order to define different line types for files. 
An individual parmatter could also define a line type on its own, but the parmatter
group also has options for prefixes, separators, and naming of parmatters (useful
in formatting and unformatting).
'''

import sys
if (sys.version_info)<(3,6): 
    # required to maintain argument order
    import warnings
    warnings.warn(  "The FormatGroupMeta metaclass and FormatGroup factory make use "
                    "of argument order preservation implemented in Python 3.6. "
                    "Unexpected behavior may occur in previous versions." )

from .meta import FormatGroupMeta
from .factory import FormatGroup