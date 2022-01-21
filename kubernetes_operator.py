#!/usr/bin/env python3

### IMPORTS ###
import aiofiles
import asyncio
import logging
import os
import sys
import yaml

from kubernetes_asyncio import client, config, watch
from kubernetes_asyncio.client.api_client import ApiClient, ApiException

from k8sobjects import CustomResourceDefinition

### GLOBALS ###

### CLASSES ###
class CannotContinueException(Exception):
    pass

### FUNCTIONS ###
async def check_for_crd(yaml_filename, create_allowed = False):
    # Load the contents of the yaml file
    async with aiofiles.open(yaml_filename, mode='r') as file:
        contents = await file.read()
        tmp_crd_input = CustomResourceDefinition(yaml.safe_load(contents))

    async with ApiClient() as api_client:
        api_instance = client.ApiextensionsV1Api(api_client)
        # List the CustomResourceDefinitions in the cluster
        try:
            api_response = await api_instance.list_custom_resource_definition()
            logging.debug("API Response - List CustomResourceDefinitions: count: %d", len(api_response.items))
        except ApiException as ex:
            logging.error("Failed to List CustomResourceDefinitions: %s", ex)

        # Check to see if the one we're looking for is already there.
        # FIXME: Should this compare the entire installed and provided CustomResourceDefinitions?
        for tmp_crd_api in api_response.items:
            logging.debug("Checking CustomResourceDefinition: '%s'", tmp_crd_api.metadata.name)
            if tmp_crd_api.metadata.name == tmp_crd_input.metadata.name:
                logging.info("Found CustomResourceDefinition: '%s'", tmp_crd_input.metadata.name)
                return # Found the CRD, so short circuit by leave this check function

        # If the CustomResourceDefinition isn't already installed...
        if create_allowed:
            # ...create the CustomResourceDefinition if allowed...
            try:
                api_response = await api_instance.create_custom_resource_definition(tmp_crd_input.get_k8sapi_object())
                logging.debug("API Response - Create CustomResourceDefinition: %s", api_response)
            except ApiException as ex:
                logging.error("Failed to Create CustomResourceDefinition: %s", ex)
                raise CannotContinueException()
        else:
            # ...otherwise just raise an error.
            logging.error(
                "Could not find CustomResourceDefinition '%s', and not allowed to create it.",
                tmp_crd_input.metadata.name
            )
            raise CannotContinueException()

async def watch_namespaces():
    async with client.ApiClient() as api_client:
        api_instance = client.CoreV1Api(api_client)
        async with watch.Watch().stream(api_instance.list_namespace) as stream:
            async for event in stream:
                logging.info("Namespace Event - Type: %s, Name: %s", event['type'], event['object'].metadata.name)

async def watch_pods():
    async with client.ApiClient() as api_client:
        api_instance = client.CoreV1Api(api_client)
        async with watch.Watch().stream(api_instance.list_pod_for_all_namespaces) as stream:
            async for event in stream:
                logging.info(
                    "Pod Event - Type: %s, Name: %s, Namespace: %s",
                    event['type'],
                    event['object'].metadata.name,
                    event['object'].metadata.namespace
                )

async def watch_colorexamples():
    # NOTE: Each of these "list_*" methods returns a list of all of the objects on the cluster when the watch is started.
    #       Also, the "list_cluster_custom_object" doesn't just list CustomResources that are "cluster level", but also
    #       lists (and gets events for) the namespaced CustomResources too.  This means one cluster wide watcher can be
    #       used instead of a watcher for each namespace.
    # FIXME: Provide a config that allows the specifying of specific namespaces to watch.
    async with client.ApiClient() as api_client:
        api_instance = client.CustomObjectsApi(api_client)
        async with watch.Watch().stream(api_instance.list_cluster_custom_object, "operators.kneedeep.io", "v1", "colorexamples") as stream:
        #async with watch.Watch().stream(api_instance.list_namespaced_custom_object, "operators.kneedeep.io", "v1", "default", "colorexamples") as stream:
            async for event in stream:
                logging.info(
                    "ColorExample Event - Type: %s, Object: %s",
                    event['type'],
                    event['object']
                )

### MAIN ###
async def main():
    # Get Environment Variables
    debug_logging = True if os.getenv('DEBUG') else False
    crd_create_allowed = True if os.getenv('CRD_CREATE') else False
    debug_logging = True
    crd_create_allowed = False

    # Setup Logging
    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(
        format = log_format,
        level = (logging.DEBUG if debug_logging else logging.INFO)
    )

    # FIXME: Setup proper SIGNAL (e.g. SIG-TERM) handling here.

    # FIXME: Remove override later (or make is a separate config)
    logging.getLogger('kubernetes').setLevel(logging.INFO)
    logging.getLogger('kubernetes_asyncio').setLevel(logging.INFO)

    # Wrapping in a big fat try/except to error out so kubernetes knows something errored (e.g. sys.exit(1))
    try:
        # Prepare connection information for Kubernetes
        await config.load_kube_config()

        # Check for existence of CustomResourceDefinitions (CRDs) needed by this operator
        await check_for_crd("manifests/colorexample-crd.yaml", create_allowed = crd_create_allowed)

        # FIXME: REMOVE LATER: Trying to watch namespaces and pods
        watcher_coroutines = []
        #watcher_coroutines.append(asyncio.ensure_future(watch_namespaces()))
        #watcher_coroutines.append(asyncio.ensure_future(watch_pods()))
        watcher_coroutines.append(asyncio.ensure_future(watch_colorexamples()))

        # FIXME: Check for and read CustomResource (CR) from CRD
        # FIXME: FUTURE: How to handle k8s streaming events for the CRs?

        # FIXME: Based on CR, figure out where to check for deployed resources

        # FIXME: Deploy new versions of the resources

        # FIXME: Should the operator check for status of deployed resources?

        # FIXME: Add all of the "watch_*" coroutines to a list and then await them all here at the end.
        for watcher in watcher_coroutines:
            logging.info("Watcher Coroutine running: %s", watcher)
        for watcher in watcher_coroutines:
            logging.info("Waiting for watcher to finish: %s", watcher)
            await watcher
    except CannotContinueException as ex:
        # If we get here, things went really bad.  This is to force a failure condition in kubernetes.
        logging.error("Caught CannotContinueException, so something went really bad.  Exiting unhappy.")
        sys.exit(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main()) # FIXME: Should this be "run_until_complete" or more of a run forever?
    loop.close()
