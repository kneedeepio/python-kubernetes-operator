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
            raise TypeError

        # FIXME: Only supporting attributes that are currently being used.
        self._name = None
        if 'name' in manifest_dict:
            self.name = manifest_dict['name']

        self._labels = None
        if 'labels' in manifest_dict:
            # This should be a dictionary of strings as key value pairs
            self.labels = manifest_dict['labels']

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
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, value):
        if not isinstance(value, dict):
            raise TypeError
        self._labels = value

    def get_k8sapi_object(self):
        self.logger.debug("get_k8sapi_object - None")
        tmp_obj = client.V1ObjectMeta()
        tmp_obj.name = self.name
        tmp_obj.labels = self.labels
        return tmp_obj