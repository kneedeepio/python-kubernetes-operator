#!/usr/bin/env python3

### IMPORTS ###
import aiofiles
import asyncio
import logging
#import os
import yaml

from string import Template

from operator_utils import DeploymentWrapper

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###

### MAIN ###
async def main():
    # Get Environment Variables
    #debug_logging = os.getenv('DEBUG')
    debug_logging = True

    # Setup Logging
    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(
        format = log_format,
        level = (logging.DEBUG if debug_logging else logging.INFO)
    )

    yaml_filename = "./manifests/colorexample_deployment.template.yaml"

    # FIXME: Load the template file into a string
    async with aiofiles.open(yaml_filename, mode='r') as file:
        contents = await file.read()
        template = Template(contents)

    # FIXME: Do the template thing on the template string
    # ce_deployment = template.substitute(
    #     name = "colorexample-test2",
    #     color = "purple",
    #     version = "v0.0.3"
    # )

    values = {
        'name': "colorexample-test2",
        'color': "purple",
        'version': "v0.0.3"
    }
    ce_deployment = template.substitute(values)

    # See if we can create a Deployment from Yaml
    tmp_manifest = yaml.safe_load(ce_deployment)
    tmp_manifest_deploy = None
    if isinstance(tmp_manifest, list):
        tmp_manifest_deploy = tmp_manifest[0]
    if isinstance(tmp_manifest, dict):
        tmp_manifest_deploy = tmp_manifest

    # Load the not so template into the wrapper class
    tmp_deploy = DeploymentWrapper(tmp_manifest_deploy)
    tmp_deploy_k8s = tmp_deploy.get_k8sapi_object()

    logging.info("The thing I made: %s\n", ce_deployment)
    logging.info("The other thing I made: %s\n", tmp_manifest_deploy)
    logging.info("The not so other thing I made: %s\n", tmp_deploy)
    logging.info("The other other thing I made: %s\n", tmp_deploy_k8s)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
