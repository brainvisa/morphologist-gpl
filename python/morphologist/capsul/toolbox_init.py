
"""
Initialization code for the "morphologist toolbox" in Capsul.

This module should be imported as a "python_modules" listed in the Capsul
configuration.

It loads the BrainVisa schemas and processes schemas for metadata and
parameters completion.
"""

from capsul.schemas.brainvisa import declare_morpho_schemas

declare_morpho_schemas('morphologist.capsul')
