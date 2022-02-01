#!/usr/bin/env python3

### IMPORTS ###
import logging

from kubernetes import client

from .exceptions import ManifestEmptyException, ManifestMissingValueException

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class LabelSelector:
    def __init__(self, manifest_dict = None):
        self.logger = logging.getLogger(type(self).__name__)

        if not manifest_dict:
            raise ManifestEmptyException()

        if not isinstance(manifest_dict, dict):
            raise TypeError # FIXME: Is this the correct exception?

        # FIXME: Only supporting attributes that are currently being used.
        if 'matchLabels' in manifest_dict:
            # This should be a dictionary of strings as key value pairs
            self.match_labels = manifest_dict['matchLabels']


    @property
    def match_labels(self):
        return self._match_labels

    @match_labels.setter
    def match_labels(self, value):
        if not isinstance(value, dict):
            raise TypeError
        # FIXME: Should figure out how to check for dict(str, str) here.
        self._match_labels = value

    def get_k8sapi_object(self):
        self.logger.debug("get_k8sapi_object - None")
        return client.V1LabelSelector(
            match_labels = self.match_labels
        )
