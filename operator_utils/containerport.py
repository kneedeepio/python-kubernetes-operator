#!/usr/bin/env python3

### IMPORTS ###
import logging

from kubernetes import client

from .exceptions import ManifestEmptyException, ManifestMissingValueException

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class ContainerPort:
    def __init__(self, manifest_dict = None):
        self.logger = logging.getLogger(type(self).__name__)

        if not manifest_dict:
            raise ManifestEmptyException()

        if not isinstance(manifest_dict, dict):
            raise TypeError

        # FIXME: Only supporting attributes that are currently being used.
        if 'containerPort' in manifest_dict:
            self._container_port = manifest_dict['containerPort']
        else:
            # 'name' should always be specified in the metadata
            self.logger.error("ContainerPort missing 'containerPort'")
            raise ManifestMissingValueException("ContainerPort missing 'containerPort'")

    @property
    def container_port(self):
        return self._container_port

    @container_port.setter
    def container_port(self, value):
        if not isinstance(value, int):
            raise TypeError
        if value < 0 or value > 65535:
            raise ValueError
        self._container_port = value

    def get_k8sapi_object(self):
        self.logger.debug("get_k8sapi_object - None")
        tmp_obj = client.V1ContainerPort(
            container_port = self.container_port
        )
        return tmp_obj
