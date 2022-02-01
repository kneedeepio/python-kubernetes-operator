#!/usr/bin/env python3

### IMPORTS ###
import logging

from kubernetes import client

from .exceptions import ManifestEmptyException, ManifestMissingValueException
from .metadata import Metadata
from .podspec import PodSpec

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class PodTemplate:
    def __init__(self, manifest_dict = None):
        self.logger = logging.getLogger(type(self).__name__)

        if not manifest_dict:
            raise ManifestEmptyException()

        if not isinstance(manifest_dict, dict):
            raise TypeError

        self._metadata = None
        if 'metadata' in manifest_dict:
            self.metadata = Metadata(manifest_dict['metadata'])

        self._spec = None
        if 'spec' in manifest_dict:
            self.spec = PodSpec(manifest_dict['spec'])

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        # FIXME: Should this be able to handle both object and dict?
        if not isinstance(value, Metadata):
            raise TypeError
        self._metadata = value

    @property
    def spec(self):
        return self._spec

    @spec.setter
    def spec(self, value):
        # FIXME: Should this be able to handle both object and dict?
        if not isinstance(value, PodSpec):
            raise TypeError
        self._spec = value

    def get_k8sapi_object(self):
        self.logger.debug("get_k8sapi_crd_object start")
        tmp_deploy = client.V1PodTemplateSpec()
        # Adding optional items
        tmp_deploy.metadata = self.metadata.get_k8sapi_object(),
        tmp_deploy.spec = self.spec.get_k8sapi_object()
        return tmp_deploy
