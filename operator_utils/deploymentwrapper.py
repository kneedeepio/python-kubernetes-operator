#!/usr/bin/env python3

### IMPORTS ###
import logging

from kubernetes import client

from .exceptions import ManifestEmptyException
from .exceptions import ManifestMissingValueException
from .exceptions import ManifestSchemaInvalidTypeException
from .exceptions import ManifestWrongKindException

from .metadata import Metadata
from .deploymentspec import DeploymentSpec

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class DeploymentWrapper:
    def __init__(self, manifest_dict = None):
        self.logger = logging.getLogger(type(self).__name__)

        # Parse the YAML into a dictionary
        #if not yaml_string:
        #    raise ManifestEmptyException()
        #self.manifest = yaml.safe_load(yaml_string)

        if not manifest_dict:
            raise ManifestEmptyException()
        # FIXME: Make sure this is a dict here?
        self.manifest = manifest_dict

        # Make sure the YAML is a CRD
        if not self.manifest['kind'] == "Deployment":
            self.logger.error("Manifest with kind '%s' is not a Deployment", self.manifest['kind'])
            raise ManifestWrongKindException("Manifest not Deployment")
        # FIXME: Should there be validation of the YAML/Manifest here?
        # FIXME: Should each of the necessary sections be created if not included in the YAML?

        if 'metadata' in manifest_dict:
            self.metadata = Metadata(manifest_dict['metadata'])
        else:
            self.logger.error("Manifest missing 'metadata'")
            raise ManifestMissingValueException("Manifest missing 'metadata'")

        if 'spec' in manifest_dict:
            self.spec = DeploymentSpec(manifest_dict['spec'])
        else:
            self.logger.error("Manifest missing 'spec'")
            raise ManifestMissingValueException("Manifest missing 'spec'")

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
        if not isinstance(value, DeploymentSpec):
            raise TypeError
        self._spec = value

    def get_k8sapi_object(self):
        self.logger.debug("get_k8sapi_crd_object start")
        tmp_deploy = client.V1Deployment(
            api_version = "apps/v1",
            kind = "Deployment",
            metadata = self.metadata.get_k8sapi_object(),
            spec = self.spec.get_k8sapi_object()
        )
        return tmp_deploy
