import os
import json

from typing import Dict, List, Literal

from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models

from aliyun.constants import REGION_ID_TO_SECURITY_GROUP_ID, ZONE_ID_TO_V_SWITCH_ID


class EcsClient:

    def __init__(
            self,
            region_id: str,
            zone_id: str = None,
            resource_group_id: str = os.getenv("RESOURCE_GROUP_ID"),
            security_group_id: str = None,
            v_switch_id: str = None,
    ):
        """
        Initialize the ECS client
        """

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
        """
        Create the ECS client
        """

        config = open_api_models.Config(
            access_key_id=os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
            access_key_secret=os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'],
        )
        config.endpoint = f'ecs.{self.region_id}.aliyuncs.com'
        return Ecs20140526Client(config)

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
    ) -> List[str]:
        """
        Create ECS instances.
        """

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
        response = await self.client.run_instances_with_options_async(run_instances_request, runtime)
        instance_ids = [instance_id for instance_id in response.body.instance_id_sets.instance_id_set]
        return instance_ids

    async def describe_instance_status_async(self, instance_id: str, region_id: str = None) -> Dict[str, str]:
        """
        Describe the status of an ECS instance.
        """

        describe_instance_status_request = ecs_20140526_models.DescribeInstanceStatusRequest(
            region_id=region_id or self.region_id,
            instance_id=[instance_id],
        )
        runtime = util_models.RuntimeOptions()
        response = await self.client.describe_instance_status_with_options_async(describe_instance_status_request, runtime)
        return {
            "status": response.body.instance_statuses.instance_status[0].status,
        }

    async def describe_instance_attribute_async(
        self,
        instance_id: str,
    ) -> ecs_20140526_models.DescribeInstanceAttributeResponseBody:
        """
        Describe the attributes of an ECS instance.
        """

        describe_instance_attribute_request = ecs_20140526_models.DescribeInstanceAttributeRequest(instance_id=instance_id)
        runtime = util_models.RuntimeOptions()
        response = await self.client.describe_instance_attribute_with_options_async(
            describe_instance_attribute_request,
            runtime,
        )
        return response.body

    async def describe_instances_async(self, instance_ids: List[str]) -> List[ecs_20140526_models.DescribeInstancesResponseBodyInstancesInstance]:
        describe_instances_request = ecs_20140526_models.DescribeInstancesRequest(
            region_id=self.region_id,
            instance_ids=json.dumps(instance_ids),
        )
        runtime = util_models.RuntimeOptions()
        response = await self.client.describe_instances_with_options_async(describe_instances_request, runtime)
        return response.body.instances.instance

    async def run_command_async(
        self,
        instance_id: str | List[str],
        command_content: str,
        working_dir: str = "/root",
        username: str = "root",
        region_id: str = None,
        command_type: str = "RunShellScript",
        timeout: int = 3600,
    ) -> ecs_20140526_models.RunCommandResponseBody:
        """
        Run a command on an ECS instance.
        """

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
        response = await self.client.run_command_with_options_async(run_command_request, runtime)
        return response.body

    async def describe_invocation_result_async(
        self,
        instance_id: str,
        command_id: str,
        invoke_id: str,
        region_id: str = None,
        content_encoding: str = "PlainText",
    ) -> ecs_20140526_models.DescribeInvocationResultsResponseBodyInvocationInvocationResultsInvocationResult:
        """
        Describe the results of an invocation on an ECS instance.
        """

        describe_invocation_results_request = ecs_20140526_models.DescribeInvocationResultsRequest(
            region_id=region_id or self.region_id,
            command_id=command_id,
            invoke_id=invoke_id,
            instance_id=instance_id,
            resource_group_id=self.resource_group_id,
            content_encoding=content_encoding,
        )
        runtime = util_models.RuntimeOptions()
        response = await self.client.describe_invocation_results_with_options_async(describe_invocation_results_request, runtime)
        return response.body.invocation.invocation_results.invocation_result[0]

    async def create_disk_async(
        self,
        size: int,
        zone_id: str = None,
        disk_category: str = "cloud_auto",
        snapshot_id: str = None,
        region_id: str = None,
    ) -> ecs_20140526_models.CreateDiskResponseBody:
        """
        Create a disk on an ECS instance.
        """

        create_disk_request = ecs_20140526_models.CreateDiskRequest(
            region_id=region_id or self.region_id,
            zone_id=zone_id or self.zone_id,
            size=size,
            disk_category=disk_category,
            resource_group_id=self.resource_group_id,
            snapshot_id=snapshot_id,
        )
        runtime = util_models.RuntimeOptions()
        response = await self.client.create_disk_with_options_async(create_disk_request, runtime)
        return response.body

    async def reset_disk_async(self, disk_id: str, snapshot_id: str) -> None:
        """
        Reset a disk on an ECS instance.
        """

        reset_disk_request = ecs_20140526_models.ResetDiskRequest(
            disk_id=disk_id,
            snapshot_id=snapshot_id,
        )
        runtime = util_models.RuntimeOptions()
        await self.client.reset_disk_with_options_async(reset_disk_request, runtime)

    async def describe_disks_async(
        self,
        instance_id: str,
        disk_type: Literal["data", "system", "all"] = "data",
        region_id: str = None,
    ) -> ecs_20140526_models.DescribeDisksResponseBodyDisksDisk:
        """
        Describe the disks on an ECS instance.
        """

        describe_disks_request = ecs_20140526_models.DescribeDisksRequest(
            region_id=region_id or self.region_id,
            instance_id=instance_id,
            disk_type=disk_type,
            resource_group_id=self.resource_group_id,
        )
        runtime = util_models.RuntimeOptions()
        response = await self.client.describe_disks_with_options_async(describe_disks_request, runtime)
        return response.body.disks

    async def attach_disk_async(
        self,
        disk_id: str,
        instance_id: str,
        delete_with_instance: bool = False,
    ) -> ecs_20140526_models.AttachDiskResponseBody:
        """
        Attach a disk to an ECS instance.
        """

        attach_disk_request = ecs_20140526_models.AttachDiskRequest(
            instance_id=instance_id,
            disk_id=disk_id,
            delete_with_instance=delete_with_instance,
        )
        runtime = util_models.RuntimeOptions()
        response = await self.client.attach_disk_with_options_async(attach_disk_request, runtime)
        return response.body

    async def delete_instances_async(self, instance_id: str | List[str], region_id: str = None, amount_limit: int = 100) -> List[str]:
        """
        Delete ECS instances.
        """

        _instance_id = instance_id if isinstance(instance_id, list) else [instance_id]
        deleted_instance_ids = []
        num_left = len(_instance_id)
        while num_left > 0:
            instance_ids_to_delete = _instance_id[:amount_limit]
            delete_instances_request = ecs_20140526_models.DeleteInstancesRequest(
                region_id=region_id or self.region_id,
                force=True,
                instance_id=instance_ids_to_delete,
            )
            runtime = util_models.RuntimeOptions()
            await self.client.delete_instances_with_options_async(delete_instances_request, runtime)
            deleted_instance_ids.extend(instance_ids_to_delete)
            num_left -= len(instance_ids_to_delete)
            _instance_id = _instance_id[amount_limit:]
        return deleted_instance_ids

    async def delete_instance_async(self, instance_id: str) -> None:
        """
        Delete an ECS instance.
        """

        delete_instance_request = ecs_20140526_models.DeleteInstanceRequest(
            instance_id=instance_id,
            force=True,
        )
        runtime = util_models.RuntimeOptions()
        await self.client.delete_instance_with_options_async(delete_instance_request, runtime)

    async def create_image_async(self, instance_id: str, image_name: str) -> str:
        """
        Create an image on an ECS instance.
        """

        create_image_request = ecs_20140526_models.CreateImageRequest(
            region_id=self.region_id,
            instance_id=instance_id,
            resource_group_id=self.resource_group_id,
            image_name=image_name,
        )
        runtime = util_models.RuntimeOptions()
        create_image_response = await self.client.create_image_with_options_async(create_image_request, runtime)
        return create_image_response.body.image_id

    async def describe_images_async(self, image_id: str) -> ecs_20140526_models.DescribeImagesResponseBodyImagesImage:
        """
        Describe the images on an ECS instance.
        """

        describe_images_request = ecs_20140526_models.DescribeImagesRequest(
            region_id=self.region_id,
            resource_group_id=self.resource_group_id,
            image_id=image_id,
        )
        runtime = util_models.RuntimeOptions()
        response = await self.client.describe_images_with_options_async(describe_images_request, runtime)
        return response.body.images

    async def stop_invoke_async(
        self,
        instance_id: str,
        invoke_id: str,
        region_id: str = None,
    ) -> None:
        """
        Stop an invocation on an ECS instance.
        """

        stop_invocation_request = ecs_20140526_models.StopInvocationRequest(
            region_id=region_id or self.region_id,
            instance_id=instance_id,
            invoke_id=invoke_id,
        )
        runtime = util_models.RuntimeOptions()
        await self.client.stop_invocation_with_options_async(stop_invocation_request, runtime)

    
    async def reboot_ecs(self, instance_id: str):
        reboot_instance_request = ecs_20140526_models.RebootInstanceRequest(
            instance_id=instance_id
        )
        runtime = util_models.RuntimeOptions()
        return await self.client.reboot_instance_with_options_async(reboot_instance_request, runtime)
