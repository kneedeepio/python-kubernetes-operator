#!/usr/bin/env python3

### IMPORTS ###
import logging

from kubernetes import client

from .exceptions import ManifestEmptyException, ManifestMissingValueException

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Metadata:
    def __init__(self, manifest_dict = None):
        self.logger = logging.getLogger(type(self).__name__)

        if not manifest_dict:
            raise ManifestEmptyException()

        if not isinstance(manifest_dict, dict):
            raise TypeError # FIXME: Is this the correct exception?

        # FIXME: Only supporting attributes that are currently being used.
        if 'name' in manifest_dict:
            self.name = manifest_dict['name']
        else:
            # 'name' should always be specified in the metadata
            self.logger.error("Metadata missing 'name'")
            raise ManifestMissingValueException("Metadata missing 'name'")

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

    def get_k8sapi_object(self):
        self.logger.debug("get_k8sapi_object")
        return client.V1ObjectMeta(
            name = self.name
        )