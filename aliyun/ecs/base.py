import os
import json
import asyncio

from typing import Dict, List, Literal

from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models

from aliyun.ecs.constants import REGION_ID_TO_SECURITY_GROUP_ID, ZONE_ID_TO_V_SWITCH_ID
from aliyun.utils.rate_limit import rate_limit
from aliyun.utils.retry import retry_decorator


class EcsClient:

    def __init__(
            self,
            region_id: str,
            zone_id: str = None,
            resource_group_id: str = os.getenv("RESOURCE_GROUP_ID"),
            security_group_id: str = None,
            v_switch_id: str = None,
    ):
        self.region_id = region_id
        self.zone_id = zone_id
        self.resource_group_id = resource_group_id
        self.security_group_id = security_group_id or REGION_ID_TO_SECURITY_GROUP_ID.get(region_id)
        self.v_switch_id = v_switch_id or ZONE_ID_TO_V_SWITCH_ID.get(zone_id)

        assert self.resource_group_id, "RESOURCE_GROUP_ID is not set"
        assert self.security_group_id, "SECURITY_GROUP_ID is not set"
        assert self.v_switch_id, "V_SWITCH_ID is not set"

        self.client = self.create_client()

    def create_client(self) -> Ecs20140526Client:
        config = open_api_models.Config(
            access_key_id=os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
            access_key_secret=os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'],
        )
        config.endpoint = f'ecs.{self.region_id}.aliyuncs.com'
        return Ecs20140526Client(config)

    @retry_decorator()
    @rate_limit()
    async def create_instances_async(
        self,
        instance_name: str,
        instance_type: str,
        system_disk_size: int,
        system_disk_category: str = "cloud_auto",
        data_disk_size: int | None = None,
        data_disk_category: str = "cloud_auto",
        image_id: str = "ubuntu_22_04_x86_64_20G_alibase_20220421.vhd",
        instance_charge_type: str = "PostPaid",
        password: str = "Nobody678!",
        internet_max_bandwidth_out: int = 100,
        internet_max_bandwidth_in: int = 100,
        amount: int = 1,
    ) -> List[str] | None:

        def create_data_disk_request() -> List[ecs_20140526_models.RunInstancesRequestDataDisk] | None:
            if data_disk_size is None:
                return None

            data_disk_request = []
            if isinstance(data_disk_size, int):
                _data_disk_size = [data_disk_size]

            for size in _data_disk_size:
                data_disk_request.append(ecs_20140526_models.RunInstancesRequestDataDisk(
                    size=size,
                    category=data_disk_category,
                    delete_with_instance=False,
                ))
            return data_disk_request

        system_disk = ecs_20140526_models.RunInstancesRequestSystemDisk(
            size=system_disk_size,
            category=system_disk_category,
        )

        data_disk = create_data_disk_request()

        run_instances_request = ecs_20140526_models.RunInstancesRequest(
            instance_name=instance_name,
            instance_type=instance_type,
            system_disk=system_disk,
            data_disk=data_disk,
            image_id=image_id,
            instance_charge_type=instance_charge_type,
            password=password,
            internet_max_bandwidth_out=internet_max_bandwidth_out,
            internet_max_bandwidth_in=internet_max_bandwidth_in,
            amount=amount,
            region_id=self.region_id,
            zone_id=self.zone_id,
            resource_group_id=self.resource_group_id,
            security_group_id=self.security_group_id,
            v_switch_id=self.v_switch_id,
        )
        runtime = util_models.RuntimeOptions()
        try:
            response = await self.client.run_instances_with_options_async(run_instances_request, runtime)
            if response.status_code == 200:
                instance_ids = [instance_id for instance_id in response.body.instance_id_sets.instance_id_set]
                return instance_ids
            else:
                return None
        except Exception as error:
            print(error)
            return None

    @retry_decorator()
    @rate_limit()
    async def describe_instance_status_async(self, instance_id: str, region_id: str = None) -> Dict[str, str] | None:
        client = self.create_client()
        describe_instance_status_request = ecs_20140526_models.DescribeInstanceStatusRequest(
            region_id=region_id or self.region_id,
            instance_id=[instance_id],
        )
        runtime = util_models.RuntimeOptions()
        try:
            response = await client.describe_instance_status_with_options_async(describe_instance_status_request, runtime)
            if response.status_code == 200:
                return {
                    "status": response.body.instance_statuses.instance_status[0].status,
                }
            else:
                return None
        except Exception as error:
            print(error)
            return None

    @retry_decorator()
    @rate_limit()
    async def describe_instance_attribute_async(
        self,
        instance_id: str,
    ) -> ecs_20140526_models.DescribeInstanceAttributeResponseBody | None:
        client = self.create_client()
        describe_instance_attribute_request = ecs_20140526_models.DescribeInstanceAttributeRequest(instance_id=instance_id)
        runtime = util_models.RuntimeOptions()
        try:
            response = await client.describe_instance_attribute_with_options_async(
                describe_instance_attribute_request,
                runtime,
            )
            if response.status_code == 200:
                return response.body
            else:
                return None
        except Exception as error:
            print(error)
            return None

    async def describe_instances_async(self, instance_ids: List[str]) -> List[ecs_20140526_models.DescribeInstancesResponseBodyInstancesInstance] | None:
        describe_instances_request = ecs_20140526_models.DescribeInstancesRequest(
            region_id=self.region_id,
            instance_ids=json.dumps(instance_ids),
        )
        runtime = util_models.RuntimeOptions()
        try:
            response = await self.client.describe_instances_with_options_async(describe_instances_request, runtime)
            return response.body.instances.instance if response.status_code == 200 else None
        except Exception as error:
            print(error)

    @retry_decorator()
    @rate_limit()
    async def run_command_async(
        self,
        instance_id: str | List[str],
        command_content: str,
        working_dir: str = "/root",
        username: str = "root",
        region_id: str = None,
        command_type: str = "RunShellScript",
        timeout: int = 3600,
    ) -> Dict[str, str] | None:
        client = self.create_client()
        _instance_id = instance_id if isinstance(instance_id, list) else [instance_id]
        run_command_request = ecs_20140526_models.RunCommandRequest(
            region_id=region_id or self.region_id,
            resource_group_id=self.resource_group_id,
            type=command_type,
            command_content=command_content,
            working_dir=working_dir,
            username=username,
            instance_id=_instance_id,
            timeout=timeout,
        )
        runtime = util_models.RuntimeOptions()
        try:
            response = await client.run_command_with_options_async(run_command_request, runtime)
            return {
                "command-id": response.body.command_id,
                "invoke-id": response.body.invoke_id,
            } if response.status_code == 200 else None
        except Exception as error:
            print(error)
            return None

    @retry_decorator()
    @rate_limit()
    async def describe_invocation_result_async(
        self,
        instance_id: str,
        command_id: str,
        invoke_id: str,
        region_id: str = None,
        content_encoding: str = "PlainText",
    ) -> ecs_20140526_models.DescribeInvocationResultsResponseBodyInvocationInvocationResultsInvocationResult | None:
        client = self.create_client()
        describe_invocation_results_request = ecs_20140526_models.DescribeInvocationResultsRequest(
            region_id=region_id or self.region_id,
            command_id=command_id,
            invoke_id=invoke_id,
            instance_id=instance_id,
            resource_group_id=self.resource_group_id,
            content_encoding=content_encoding,
        )
        runtime = util_models.RuntimeOptions()
        response = await client.describe_invocation_results_with_options_async(describe_invocation_results_request, runtime)
        return response.body.invocation.invocation_results.invocation_result[0]

    @retry_decorator()
    @rate_limit()
    async def create_disk_async(
        self,
        size: int,
        zone_id: str = None,
        disk_category: str = "cloud_auto",
        snapshot_id: str = None,
        region_id: str = None,
    ) -> ecs_20140526_models.CreateDiskResponseBody | None:
        create_disk_request = ecs_20140526_models.CreateDiskRequest(
            region_id=region_id or self.region_id,
            zone_id=zone_id or self.zone_id,
            size=size,
            disk_category=disk_category,
            resource_group_id=self.resource_group_id,
            snapshot_id=snapshot_id,
        )
        runtime = util_models.RuntimeOptions()
        try:
            response = await self.client.create_disk_with_options_async(create_disk_request, runtime)
            return response.body if response.status_code == 200 else None
        except Exception as error:
            print(error)
            return None

    @retry_decorator()
    @rate_limit()
    async def reset_disk_async(self, disk_id: str, snapshot_id: str) -> str | None:
        reset_disk_request = ecs_20140526_models.ResetDiskRequest(
            disk_id=disk_id,
            snapshot_id=snapshot_id,
        )
        runtime = util_models.RuntimeOptions()
        try:
            response = await self.client.reset_disk_with_options_async(reset_disk_request, runtime)
            return response.body.request_id if response.status_code == 200 else None
        except Exception as error:
            print(error)
            return None

    @retry_decorator()
    @rate_limit()
    async def describe_disks_async(
        self,
        instance_id: str,
        disk_type: Literal["data", "system", "all"] = "data",
        region_id: str = None,
    ) -> str | None:
        describe_disks_request = ecs_20140526_models.DescribeDisksRequest(
            region_id=region_id or self.region_id,
            instance_id=instance_id,
            disk_type=disk_type,
            resource_group_id=self.resource_group_id,
        )
        runtime = util_models.RuntimeOptions()
        try:
            response = await self.client.describe_disks_with_options_async(describe_disks_request, runtime)
            return response.body.disks.disk[0].disk_id if response.status_code == 200 else None
        except Exception as error:
            print(error)
            return None

    @retry_decorator()
    @rate_limit()
    async def attach_disk_async(
        self,
        disk_id: str,
        instance_id: str,
        delete_with_instance: bool = False,
    ) -> ecs_20140526_models.AttachDiskResponseBody | None:
        attach_disk_request = ecs_20140526_models.AttachDiskRequest(
            instance_id=instance_id,
            disk_id=disk_id,
            delete_with_instance=delete_with_instance,
        )
        runtime = util_models.RuntimeOptions()
        try:
            response = await self.client.attach_disk_with_options_async(attach_disk_request, runtime)
            return response.body if response.status_code == 200 else None
        except Exception as error:
            print(error)
            return None

    @retry_decorator()
    @rate_limit()
    async def delete_instances_async(self, instance_id: str | List[str], region_id: str = None, amount_limit: int = 100) -> List[str] | None:

        _instance_id = instance_id if isinstance(instance_id, list) else [instance_id]
        deleted_instance_ids = []
        _amount = len(_instance_id)
        while _amount > 0:
            instance_ids_to_delete = _instance_id[:amount_limit]
            delete_instances_request = ecs_20140526_models.DeleteInstancesRequest(
                region_id=region_id or self.region_id,
                force=True,
                instance_id=instance_ids_to_delete,
            )
            runtime = util_models.RuntimeOptions()
            try:
                response = await self.client.delete_instances_with_options_async(delete_instances_request, runtime)
                if response.status_code == 200:
                    deleted_instance_ids.extend(instance_ids_to_delete)
                    _amount -= len(instance_ids_to_delete)
                    _instance_id = _instance_id[amount_limit:]
                else:
                    return None
            except Exception as error:
                print(error)
                return None
        return deleted_instance_ids

    @retry_decorator()
    @rate_limit()
    async def delete_instance_async(self, instance_id: str) -> str | None:
        print(f"Deleting instance: {instance_id}")
        delete_instance_request = ecs_20140526_models.DeleteInstanceRequest(
            instance_id=instance_id,
            force=True,
        )
        runtime = util_models.RuntimeOptions()
        try:
            response = await self.client.delete_instance_with_options_async(delete_instance_request, runtime)
            if response.status_code == 200:
                return instance_id
            else:
                return None
        except Exception as error:
            print(error)
            return None

    @retry_decorator()
    @rate_limit()
    async def create_image_and_wait_until_ready_async(self, instance_id: str, image_name: str) -> str | None:
        try:
            create_image_request = ecs_20140526_models.CreateImageRequest(
                region_id=self.region_id,
                instance_id=instance_id,
                resource_group_id=self.resource_group_id,
                image_name=image_name,
            )
            runtime = util_models.RuntimeOptions()
            create_image_response = await self.client.create_image_with_options_async(create_image_request, runtime)
            image_id = create_image_response.body.image_id
            print(f"Create image for {instance_id}: {image_id = }")

            while True:
                await asyncio.sleep(10)
                describe_images_request = ecs_20140526_models.DescribeImagesRequest(region_id=self.region_id, resource_group_id=self.resource_group_id, image_id=image_id)
                runtime = util_models.RuntimeOptions()
                response = await self.client.describe_images_with_options_async(describe_images_request, runtime)
                if "Available" in str(response.body):
                    break
                else:
                    print(f"Wait for image {image_id} ready...")
            return image_id
        except Exception as error:
            print(error)
            return None

    async def stop_invoke_async(
        self,
        instance_id: str,
        invoke_id: str,
        region_id: str = None,
    ) -> str | None:
        stop_invocation_request = ecs_20140526_models.StopInvocationRequest(
            region_id=region_id or self.region_id,
            instance_id=instance_id,
            invoke_id=invoke_id,
        )
        runtime = util_models.RuntimeOptions()
        try:
            response = await self.client.stop_invocation_with_options_async(stop_invocation_request, runtime)
            return response.body.instance_statuses.instance_status[0].status if response.status_code == 200 else None
        except Exception as error:
            print(error)
            return None
