#!/usr/bin/env python3

### IMPORTS ###
import logging

from kubernetes import client

from .exceptions import ManifestEmptyException, ManifestMissingValueException
from .labelselector import LabelSelector
from .podtemplate import PodTemplate

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class DeploymentSpec:
    def __init__(self, manifest_dict = None):
        self.logger = logging.getLogger(type(self).__name__)

        if not manifest_dict:
            raise ManifestEmptyException()

        if not isinstance(manifest_dict, dict):
            raise TypeError

        # FIXME: Only supporting attributes that are currently being used.
        # NOTE: The V1* objects from the Kubernetes client can't be instantiated
        #       empty, so I'm not going to allow it either.
        if 'replicas' in manifest_dict:
            self.replicas = manifest_dict['replicas']
        else:
            # 'replicas' should always be specified in the deployment spec
            # Technically, 'replicas' is optional and defaults to 1, but really
            # should be specified so there's no confusion.
            self.logger.error("Deployment Spec missing 'replicas'")
            raise ManifestMissingValueException("Deployment Spec missing 'replicas'")

        if 'selector' in manifest_dict:
            self.selector = LabelSelector(manifest_dict['selector'])
        else:
            # 'selector' should always be specified in the deployment spec
            self.logger.error("Deployment Spec missing 'selector'")
            raise ManifestMissingValueException("Deployment Spec missing 'selector'")

        if 'template' in manifest_dict:
            self.template = PodTemplate(manifest_dict['template'])
        else:
            # 'selector' should always be specified in the deployment spec
            self.logger.error("Deployment Spec missing 'template'")
            raise ManifestMissingValueException("Deployment Spec missing 'template'")

    @property
    def replicas(self):
         return self._replicas

    @replicas.setter
    def replicas(self, value):
        if not isinstance(value, int):
            raise TypeError
        if value < 0:
            raise ValueError
        self._replicas = value

    @property
    def selector(self):
         return self._selector

    @selector.setter
    def selector(self, value):
        if not isinstance(value, LabelSelector):
            raise TypeError
        self._selector = value

    @property
    def template(self):
         return self._template

    @template.setter
    def template(self, value):
        if not isinstance(value, PodTemplate):
            raise TypeError
        self._template = value

    def get_k8sapi_object(self):
        self.logger.debug("get_k8sapi_object - None")
        return client.V1DeploymentSpec(
            replicas = self.replicas,
            selector = self.selector.get_k8sapi_object(),
            template = self.template.get_k8sapi_object()
        )