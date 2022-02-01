#!/usr/bin/env python3

### IMPORTS ###
import logging

from kubernetes import client

from .exceptions import ManifestEmptyException, ManifestMissingValueException
from .env import EnvVar
from .containerport import ContainerPort

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Container:
    def __init__(self, manifest_dict = None):
        self.logger = logging.getLogger(type(self).__name__)

        if not manifest_dict:
            raise ManifestEmptyException()

        if not isinstance(manifest_dict, dict):
            raise TypeError

        # FIXME: Only supporting attributes that are currently being used.
        # NOTE: The V1* objects from the Kubernetes client can't be instantiated
        #       empty, so I'm not going to allow it either.
        if 'name' in manifest_dict:
            self.name = manifest_dict['name']
        else:
            self.logger.error("Container missing 'name'")
            raise ManifestMissingValueException("Container missing 'name'")

        self._image = None
        if 'image' in manifest_dict:
            self.image = manifest_dict['image']

        self._env = None
        if 'env' in manifest_dict:
            tmp_list = []
            for item in manifest_dict['env']:
                tmp_list.append(EnvVar(item)) # FIXME: Need to make this
            self.env = tmp_list

        self._ports = None
        if 'ports' in manifest_dict:
            tmp_list = []
            for item in manifest_dict['ports']:
                tmp_list.append(ContainerPort(item)) # FIXME: Need to make this
            self.ports = tmp_list

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
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        if not isinstance(value, str):
            raise TypeError
        if len(value) < 3:
            raise ValueError
        self._image = value

    @property
    def env(self):
        return self._env

    @env.setter
    def env(self, value):
        if not isinstance(value, list):
            raise TypeError
        for item in value:
            if not isinstance(item, EnvVar):
                raise TypeError
        self._env = value

    @property
    def ports(self):
        return self._ports

    @ports.setter
    def ports(self, value):
        if not isinstance(value, list):
            raise TypeError
        for item in value:
            if not isinstance(item, ContainerPort):
                raise TypeError
        self._ports = value

    def get_k8sapi_object(self):
        self.logger.debug("get_k8sapi_object - None")
        tmp_list_env = []
        for item in self.env:
            tmp_list_env.append(item.get_k8sapi_object())
        tmp_list_ports = []
        for item in self.ports:
            tmp_list_ports.append(item.get_k8sapi_object())
        tmp_obj = client.V1Container(
            name = self.name
        )
        tmp_obj.image = self.image,
        tmp_obj.env = tmp_list_env
        tmp_obj.ports = tmp_list_ports
        return tmp_obj
