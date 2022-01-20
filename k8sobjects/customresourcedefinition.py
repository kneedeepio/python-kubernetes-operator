#!/usr/bin/env python3

### IMPORTS ###
import logging

from kubernetes import client

from .exceptions import ManifestEmptyException
from .exceptions import ManifestMissingValueException
from .exceptions import ManifestSchemaInvalidTypeException
from .exceptions import ManifestWrongKindException
from .metadata import Metadata

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class CustomResourceDefinition:
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
        if not self.manifest['kind'] == "CustomResourceDefinition":
            self.logger.error("Manifest with kind '%s' is not a CustomResourceDefinition", self.manifest['kind'])
            raise ManifestWrongKindException("Manifest not CustomResourceDefinition")
        # FIXME: Should there be validation of the YAML/Manifest here?
        # FIXME: Should each of the necessary sections be created if not included in the YAML?

        if not 'metadata' in manifest_dict:
            self.logger.error("Manifest missing 'metadata'")
            raise ManifestMissingValueException("Manifest missing 'metadata'")
        self.metadata = Metadata(manifest_dict['metadata'])

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
    def name(self):
        return self.metadata.name

    @name.setter
    def name(self, value):
        # Checked in the metadata class
        #if not isinstance(value, str):
        #    raise TypeError
        #if len(value) < 3:
        #    raise ValueError
        self.metadata.name = value

    @property
    def group(self):
        return self.manifest['spec']['group']

    @group.setter
    def group(self, value):
        if not isinstance(value, str):
            raise TypeError
        if len(value) < 3:
            raise ValueError
        self.manifest['spec']['group'] = value

    @property
    def names_singular(self):
        return self.manifest['spec']['names']['singular']

    @names_singular.setter
    def names_singular(self, value):
        if not isinstance(value, str):
            raise TypeError
        if len(value) < 3:
            raise ValueError
        self.manifest['spec']['names']['singular'] = value

    @property
    def names_plural(self):
        return self.manifest['spec']['names']['plural']

    @names_plural.setter
    def names_plural(self, value):
        if not isinstance(value, str):
            raise TypeError
        if len(value) < 3:
            raise ValueError
        self.manifest['spec']['names']['plural'] = value

    @property
    def names_kind(self):
        return self.manifest['spec']['names']['kind']

    @names_kind.setter
    def names_kind(self, value):
        if not isinstance(value, str):
            raise TypeError
        if len(value) < 3:
            raise ValueError
        self.manifest['spec']['names']['kind'] = value

    @property
    def names_shortnames(self):
        return self.manifest['spec']['names']['shortNames']

    @names_shortnames.setter
    def names_shortnames(self, value):
        if not isinstance(value, list):
            raise TypeError
        if len(value) < 1:
            raise ValueError
        # FIXME: Should the list be checked to make sure it contains strings?
        self.manifest['spec']['names']['shortNames'] = value

    # FIXME: Add properties to handle the versions / schemas of the CRD

    # FIXME: Make this handle all of the values in a CRD manifest
    def get_k8sapi_object(self):
        self.logger.debug("get_k8sapi_crd_object start")
        #tmp_metadata = client.V1ObjectMeta(
        #    name = self.name
        #)
        tmp_spec_names = client.V1CustomResourceDefinitionNames(
            plural = self.names_plural,
            singular = self.names_singular,
            kind = self.names_kind,
            short_names = self.names_shortnames
        )
        tmp_spec = client.V1CustomResourceDefinitionSpec(
            group = self.group,
            scope = "Namespaced",
            versions = [],
            names = tmp_spec_names
        )
        for tmp_spec_ver in self.manifest['spec']['versions']:
            # Walk the spec.versions using the V1JSONSchemaProps.
            tmp_oa3_schema = self._walk_spec_chunk(tmp_spec_ver['schema']['openAPIV3Schema'])
            # Create the 'spec.versions' item, working back up the tree.
            tmp_schema = client.V1CustomResourceValidation(
                open_apiv3_schema = tmp_oa3_schema
            )
            tmp_version = client.V1CustomResourceDefinitionVersion(
                name = tmp_spec_ver['name'],
                served = tmp_spec_ver['served'],
                storage = tmp_spec_ver['storage'],
                schema = tmp_schema
            )
            tmp_spec.versions.append(tmp_version)
        tmp_crd = client.V1CustomResourceDefinition(
            api_version = "apiextensions.k8s.io/v1",
            kind = "CustomResourceDefinition",
            metadata = self.metadata.get_k8sapi_object(),
            spec = tmp_spec
        )
        return tmp_crd

    # This method walks through the spec in the 'versions' data structure,
    # recursively converting the chunk using the V1JSONSchemaProps class
    def _walk_spec_chunk(self, chunk):
        self.logger.debug("_walk_spec_chunk start - chunk: %s", chunk)
        if chunk['type'] == "string":
            return client.V1JSONSchemaProps(
                type = "string",
                enum = chunk['enum'] if 'enum' in chunk else None
            )

        # FIXME: Handle Integers

        # FIXME: Handle Lists

        if chunk['type'] == "object":
            tmp_properties = {}
            for property_name in chunk['properties']:
                tmp_properties[property_name] = self._walk_spec_chunk(chunk['properties'][property_name])
            return client.V1JSONSchemaProps(
                type = "object",
                properties = tmp_properties
            )

        self.logger.error("Invalid type used in CRD Schema: %s", chunk['type'])
        raise ManifestSchemaInvalidTypeException("Invalid Schema Type")
