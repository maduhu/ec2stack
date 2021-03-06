#!/usr/bin/env python
# encoding: utf-8

import uuid

from flask import current_app

from ec2stack import errors
from ec2stack import helpers
from ec2stack.providers import cloudstack
from ec2stack.providers.cloudstack import requester, disk_offerings, zones


volume_error_to_aws = {
    'unable to find a snapshot': errors.invalid_snapshot_id,
    'Unable to aquire volume with ID': errors.invalid_volume_id,
    'Please specify a volume that is not attached': errors.volume_attached,
    'The specified volume is not attached': errors.volume_detached,
    'Invalid parameter virtualmachineid': errors.invalid_instance_id,
    'Invalid parameter id': errors.invalid_volume_id
}


@helpers.authentication_required
def describe_volumes():
    args = {'command': 'listVolumes'}
    response = cloudstack.describe_item(
        args, 'volume', errors.invalid_volume_id, 'VolumeId'
    )

    return _describe_volumes_response(
        response
    )


def _describe_volumes_response(response):
    return {
        'template_name_or_list': 'volumes.xml',
        'response_type': 'DescribeVolumesResponse',
        'response': response,
    }


@helpers.authentication_required
def create_volume():
    helpers.require_atleast_one_parameter(['SnapshotId', 'Size'])
    response = _create_volume_request()
    return _create_volume_response(response)


def _create_volume_request():
    args = {}

    if helpers.contains_parameter('SnapshotId'):
        args['snapshotid'] = helpers.get('SnapshotId')

    else:
        args['size'] = helpers.get('Size')
        args['diskofferingid'] = disk_offerings.get_disk_offering(
            current_app.config['CLOUDSTACK_CUSTOM_DISK_OFFERING']
        )['id']

    zone_name = helpers.get('AvailabilityZone')
    zone_id = zones.get_zone(zone_name)['id']

    args['zoneid'] = zone_id
    args['command'] = 'createVolume'
    args['name'] = uuid.uuid4()

    response = requester.make_request_async(args)

    return response


def _create_volume_response(response):
    if 'errortext' in response:
        helpers.error_to_aws(response, volume_error_to_aws)

    response = response['volume']
    return {
        'template_name_or_list': 'create_volume.xml',
        'response_type': 'CreateVolumeResponse',
        'response': response
    }


@helpers.authentication_required
def attach_volume():
    helpers.require_parameters(['VolumeId', 'InstanceId', 'Device'])
    response = _attach_volume_request()
    return _attach_volume_response(response)


def _attach_volume_request():
    args = {}

    volume_id = helpers.get('VolumeId')
    instance_id = helpers.get('InstanceId')
    device = helpers.get('Device')

    args['id'] = volume_id
    args['command'] = 'attachVolume'
    args['virtualmachineid'] = instance_id
    args['device'] = device

    response = requester.make_request_async(args)

    return response


def _attach_volume_response(response):
    if 'errortext' in response:
        helpers.error_to_aws(response, volume_error_to_aws)

    response = response['volume']
    return {
        'template_name_or_list': 'volume_attachment.xml',
        'response_type': 'AttachVolumeResponse',
        'response': response
    }


@helpers.authentication_required
def detach_volume():
    helpers.require_parameters(['VolumeId'])
    response = _detach_volume_request()
    return _detach_volume_response(response)


def _detach_volume_request():
    args = {}

    volume_id = helpers.get('VolumeId')

    if helpers.contains_parameter('InstanceId'):
        args['virtualmachineid'] = helpers.get('InstanceId')
    if helpers.contains_parameter('Device'):
        args['deviceid'] = helpers.get('Device')

    args['id'] = volume_id
    args['command'] = 'detachVolume'

    response = requester.make_request_async(args)

    return response


def _detach_volume_response(response):
    if 'errortext' in response:
        helpers.error_to_aws(response, volume_error_to_aws)

    response = response['volume']
    return {
        'template_name_or_list': 'volume_attachment.xml',
        'response_type': 'DetachVolumeResponse',
        'response': response
    }


@helpers.authentication_required
def delete_volume():
    helpers.require_parameters(['VolumeId'])
    response = _delete_volume_request()

    return _delete_volume_response(response)


def _delete_volume_request():
    args = {'id': helpers.get('VolumeId'), 'command': 'deleteVolume'}

    response = requester.make_request(args)
    response = response['deletevolumeresponse']

    return response


def _delete_volume_response(response):
    if 'errortext' in response:
        helpers.error_to_aws(response, volume_error_to_aws)

    return {
        'template_name_or_list': 'status.xml',
        'response_type': 'DeleteVolumeResponse',
        'return': 'true'
    }
