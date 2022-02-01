#!/usr/bin/env python3

### IMPORTS ###
import logging

from kubernetes import client

from .exceptions import ManifestEmptyException, ManifestMissingValueException

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class EnvVar:
    def __init__(self, manifest_dict = None):
        self.logger = logging.getLogger(type(self).__name__)

        if not manifest_dict:
            raise ManifestEmptyException()

        if not isinstance(manifest_dict, dict):
            raise TypeError

        # FIXME: Only supporting attributes that are currently being used.
        if 'name' in manifest_dict:
            self.name = manifest_dict['name']
        else:
            # 'name' should always be specified in the metadata
            self.logger.error("EnvVar missing 'name'")
            raise ManifestMissingValueException("EnvVar missing 'name'")

        self._value = None
        if 'value' in manifest_dict:
            # This should be a dictionary of strings as key value pairs
            self.value = manifest_dict['value']

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError
        if len(value) < 3:
            raise ValueError
        self._name = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, str):
            raise TypeError
        self._value = value

    def get_k8sapi_object(self):
        self.logger.debug("get_k8sapi_object - None")
        tmp_obj = client.V1EnvVar(
            name = self.name
        )
        tmp_obj.value = self.value
        return tmp_obj
