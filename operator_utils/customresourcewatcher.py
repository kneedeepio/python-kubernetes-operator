#!/usr/bin/env python3

### IMPORTS ###
import asyncio
import logging

from kubernetes_asyncio import client, watch

from .customresourceevent import CustomResourceEvent

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class CustomResourceWatcherCluster:
    def __init__(self, group, version, plural, queue):
        self.logger = logging.getLogger(type(self).__name__)

        self.group = group
        self.version = version
        self.plural = plural
        self._queue = queue

    async def watcher(self):
        # NOTE: Each of these "list_*" methods returns a list of all of the objects on the cluster when the watch is started.
        #       Also, the "list_cluster_custom_object" doesn't just list CustomResources that are "cluster level", but also
        #       lists (and gets events for) the namespaced CustomResources too.  This means one cluster wide watcher can be
        #       used instead of a watcher for each namespace.
        # FIXME: Provide a config that allows the specifying of specific namespaces to watch.
        async with client.ApiClient() as api_client:
            api_instance = client.CustomObjectsApi(api_client)
            async with watch.Watch().stream(api_instance.list_cluster_custom_object, self.group, self.version, self.plural) as stream:
            #async with watch.Watch().stream(api_instance.list_namespaced_custom_object, "operators.kneedeep.io", "v1", "default", "colorexamples") as stream:
                async for event in stream:
                    logging.debug(
                        "ColorExample Event - Type: %s, Object: %s",
                        event['type'],
                        event['object']
                    )
                    logging.info(
                        "ColorExample Event - Type: %s, Name: %s, Namespace: %s",
                        event['type'],
                        event['object']['metadata']['name'],
                        event['object']['metadata']['namespace']
                    )
                    await self._queue.put(CustomResourceEvent(
                        self.group,
                        self.version,
                        self.plural,
                        event['object']['metadata']['namespace'],
                        event['object']['metadata']['name'],
                        event['type']
                    ))
