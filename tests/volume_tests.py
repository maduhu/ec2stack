#!/usr/bin/env python
# encoding: utf-8

import mock
import json

from ec2stack.helpers import read_file, generate_signature
from . import Ec2StackAppTestCase


class VolumeTestCase(Ec2StackAppTestCase):

    def test_describe_volumes(self):
        data = self.get_example_data()
        data['Action'] = 'DescribeVolumes'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_key_pairs.json'
        )
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            response = self.post(
                '/',
                data=data
            )

        self.assert_ok(response)
        assert 'DescribeVolumesResponse' in response.data

    def test_describe_volume_by_id(self):
        data = self.get_example_data()
        data['Action'] = 'DescribeVolumes'
        data['VolumeId.1'] = 'de2d8297-eaaf-4e81-8ffe-97f37ddbbde5'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_volumes.json'
        )
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            response = self.post(
                '/',
                data=data
            )

        self.assert_ok(response)
        assert 'DescribeVolumesResponse' in response.data
        assert 'de2d8297-eaaf-4e81-8ffe-97f37ddbbde5' in response.data

    def test_invalid_describe_volume_by_id(self):
        data = self.get_example_data()
        data['Action'] = 'DescribeVolumes'
        data['VolumeId.1'] = 'invalid-volume-id'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_volumes.json'
        )
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            response = self.post(
                '/',
                data=data
            )

        self.assert_bad_request(response)
        assert 'InvalidVolume.NotFound' in response.data

    def test_empty_response_describe_volume_by_id(self):
        data = self.get_example_data()
        data['Action'] = 'DescribeVolumes'
        data['VolumeId.1'] = 'invalid-volume-id'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/empty_describe_volumes.json'
        )
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            response = self.post(
                '/',
                data=data
            )

        self.assert_bad_request(response)
        assert 'InvalidVolume.NotFound' in response.data

    def test_create_volume_by_size(self):
        data = self.get_example_data()
        data['Action'] = 'CreateVolume'
        data['Size'] = '80'
        data['AvailabilityZone'] = 'Sandbox-simulator'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/create_volume_response.json'
        )
        get.return_value.status_code = 200

        get_disk_offering = mock.Mock()
        get_disk_offering.return_value = json.loads(read_file(
            'tests/data/disk_offering_search.json'
        ))

        get_zone = mock.Mock()
        get_zone.return_value = json.loads(read_file(
            'tests/data/zones_search.json'
        ))

        with mock.patch('requests.get', get):
            with mock.patch(
                    'ec2stack.providers.cloudstack.disk_offerings.get_disk_offering',
                    get_disk_offering
            ):
                with mock.patch(
                    'ec2stack.providers.cloudstack.zones.get_zone',
                    get_zone
                ):
                    response = self.post(
                        '/',
                        data=data
                    )

        self.assert_ok(response)
        assert 'CreateVolumeResponse' in response.data

    def test_create_volume_by_snapshot(self):
        data = self.get_example_data()
        data['Action'] = 'CreateVolume'
        data['SnapshotId'] = '076166a1-9f6e-11e3-b8df-3c075456b21a'
        data['AvailabilityZone'] = 'Sandbox-simulator'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/create_volume_response.json'
        )
        get.return_value.status_code = 200

        get_zone = mock.Mock()
        get_zone.return_value = json.loads(read_file(
            'tests/data/zones_search.json'
        ))

        with mock.patch('requests.get', get):
            with mock.patch(
                'ec2stack.providers.cloudstack.zones.get_zone',
                get_zone
            ):
                response = self.post(
                    '/',
                    data=data
                )

        self.assert_ok(response)
        assert 'CreateVolumeResponse' in response.data

    def test_create_volume_invalid_snapshot(self):
        data = self.get_example_data()
        data['Action'] = 'CreateVolume'
        data['SnapshotId'] = 'invalid-snapshot-id'
        data['AvailabilityZone'] = 'Sandbox-simulator'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get_request = mock.Mock()
        get_request.return_value.text = read_file(
            'tests/data/create_volume_invalid_snapshot_response.json'
        )
        get_request.return_value.status_code = 431

        get_zone = mock.Mock()
        get_zone.return_value = json.loads(read_file(
            'tests/data/zones_search.json'
        ))

        with mock.patch('requests.get', get_request):
                with mock.patch(
                    'ec2stack.providers.cloudstack.zones.get_zone',
                    get_zone
                ):
                    response = self.post(
                        '/',
                        data=data
                    )

        self.assert_bad_request(response)
        assert 'InvalidSnapshot.NotFound' in response.data

    def test_create_volume_invalid_zone(self):
        data = self.get_example_data()
        data['Action'] = 'CreateVolume'
        data['SnapshotId'] = '076166a1-9f6e-11e3-b8df-3c075456b21a'
        data['AvailabilityZone'] = 'Sandbox-simulator'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/empty_describe_zone.json'
        )
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            response = self.post(
                '/',
                data=data
            )

        self.assert_bad_request(response)
        assert 'InvalidZone.NotFound' in response.data

    def test_create_volume_invalid_disk_offering(self):
        data = self.get_example_data()
        data['Action'] = 'CreateVolume'
        data['Size'] = '80'
        data['AvailabilityZone'] = 'Sandbox-simulator'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get_request = mock.Mock()
        get_request.return_value.text = read_file(
            'tests/data/empty_describe_disk_offerings.json'
        )
        get_request.return_value.status_code = 200

        with mock.patch('requests.get', get_request):
            response = self.post(
                '/',
                data=data
            )

        self.assert_bad_request(response)
        assert 'InvalidDiskOffering.NotFound' in response.data

    def test_delete_volume(self):
        data = self.get_example_data()
        data['Action'] = 'DeleteVolume'
        data['VolumeId'] = 'volumeid'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get_request = mock.Mock()
        get_request.return_value.text = read_file(
            'tests/data/delete_volume_response.json'
        )
        get_request.return_value.status_code = 200

        with mock.patch('requests.get', get_request):
            response = self.post(
                '/',
                data=data
            )

        self.assert_ok(response)
        assert 'DeleteVolumeResponse' in response.data

    def test_delete_volume_invalid_volume_id(self):
        data = self.get_example_data()
        data['Action'] = 'DeleteVolume'
        data['VolumeId'] = 'volumeid'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get_request = mock.Mock()
        get_request.return_value.text = read_file(
            'tests/data/invalid_volume_id.json'
        )
        get_request.return_value.status_code = 200

        with mock.patch('requests.get', get_request):
            response = self.post(
                '/',
                data=data
            )

        self.assert_bad_request(response)
        assert 'InvalidVolume.NotFound' in response.data