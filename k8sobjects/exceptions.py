#!/usr/bin/env python3

### IMPORTS ###

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class ManifestEmptyException(Exception):
    pass

class ManifestMissingValueException(Exception):
    pass

class ManifestSchemaInvalidTypeException(Exception):
    pass

class ManifestWrongKindException(Exception):
    pass