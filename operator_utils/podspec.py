#!/usr/bin/env python3

### IMPORTS ###
import logging

from kubernetes import client

from .exceptions import ManifestEmptyException, ManifestMissingValueException
from .container import Container

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class PodSpec:
    def __init__(self, manifest_dict = None):
        self.logger = logging.getLogger(type(self).__name__)

        if not manifest_dict:
            raise ManifestEmptyException()

        if not isinstance(manifest_dict, dict):
            raise TypeError

        if 'containers' in manifest_dict:
            tmp_list = []
            for item in manifest_dict['containers']:
                tmp_list.append(Container(item))
            self.containers = tmp_list
        else:
            self.logger.error("PodSpec missing 'containers'")
            raise ManifestMissingValueException("PodSpec missing 'containers'")

    @property
    def containers(self):
        return self._containers

    @containers.setter
    def containers(self, value):
        if not isinstance(value, list):
            raise TypeError
        for item in value:
            if not isinstance(item, Container):
                raise TypeError
        self._containers = value

    def get_k8sapi_object(self):
        self.logger.debug("get_k8sapi_object start")
        # FIXME: Need to handle the list here too
        tmp_list = []
        for item in self.containers:
            tmp_list.append(item.get_k8sapi_object())
        tmp_obj = client.V1PodSpec(
            containers = tmp_list
        )
        return tmp_obj
