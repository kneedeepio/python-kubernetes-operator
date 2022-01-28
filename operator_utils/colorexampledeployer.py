#!/usr/bin/env python3

### IMPORTS ###
import asyncio
import logging

from kubernetes_asyncio import client, watch

from .customresourceevent import CustomResourceEvent

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class ColorExampleDeployer:
    def __init__(self, queue):
        self.logger = logging.getLogger(type(self).__name__)
        self._queue = queue
        self._running = True

    def shutdown(self):
        self.logger.debug("shutdown - None")
        self._running = False

    async def delete_resources(self, name, namespace):
        self.logger.debug("delete_resources - Name: %s, Namespace: %s", name, namespace)
        # Delete all the resource for ColorExample, in this case the deployment and service
        async with client.ApiClient() as api_client:
            api_instance = client.CoreV1Api(api_client)
            await api_instance.delete_namespaced_service(name, namespace)
        async with client.ApiClient() as api_client:
            api_instance = client.AppsV1Api(api_client)
            await api_instance.delete_namespaced_deployment(name, namespace)

    async def worker(self):
        self.logger.debug("worker - None")
        # FIXME: This worker part should be moved to a CustomResourceDeployer that can pick which deployer to use based
        #        on the event group, version, plural

        # FIXME: Make a looper that gets a CustomResourceEvent off the queue
        #        and either creates/updates the deployment and service for the
        #        ColorExample application or deletes the deployment and service.
        while self._running:
            # FIXME: Check the queue for a CRE
            tmp_cre = await self._queue.get()

            # FIXME: If DELETED, check if the deployment and service exist.  If so, delete them.
            if tmp_cre['event_type'] == "DELETED":
                await self.delete_resources(tmp_cre['name'], tmp_cre['namespace'])

            # FIXME: If ADDED or MODIFIED, generate the needed resources and push them.
            # FIXME: May need to change to a "check if exists and modify" for MODIFIED.
            elif tmp_cre['event_type'] == "ADDED" or tmp_cre['event_type'] == "MODIFIED":
                pass

            else:
                self.logger.debug("Invalid event type in CustomResourceEvent: %s", tmp_cre['event_type'])

        self.logger.debug("worker - Done")
