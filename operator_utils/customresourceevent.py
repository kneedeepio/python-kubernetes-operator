#!/usr/bin/env python3

### IMPORTS ###
import asyncio
import logging

from kubernetes_asyncio import client

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class CustomResourceEvent:
    def __init__(self, group, version, plural, namespace, name, event_type):
        self.logger = logging.getLogger(type(self).__name__)

        self.group = group
        self.version = version
        self.plural = plural
        self.namespace = namespace
        self.name = name
        self.event_type = event_type
