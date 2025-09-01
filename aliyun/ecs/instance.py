import os

from typing import Any, Dict, List

from alibabacloud_ecs20140526 import models as ecs_20140526_models

from aliyun.ecs.base import EcsClient
from aliyun.utils.rate_limit import rate_limit
from aliyun.utils.retry import retry_decorator


class EcsInstance(EcsClient):
    instance_id: str | None = None

    def __init__(
        self,
        # most important parameters
        instance_name: str,
        instance_type: str,
        system_disk_size: int,
        data_disk_size: None | int | List[int] = None,
        image_id: str = "ubuntu_22_04_x64_20G_alibase_20250324.vhd",
        region_id: str = "cn-shanghai",
        zone_id: str = "cn-shanghai-b",
        # optional parameters
        resource_group_id: str = os.env.get("RESOURCE_GROUP_ID"),
        security_group_id: str = None,
        v_switch_id: str = None,
        internet_max_bandwidth_out: int = 100,
        internet_max_bandwidth_in: int = 100,
        password: str = "Qwen678!",
        system_disk_category: str = "cloud_auto",
        data_disk_category: str = "cloud_auto",
        instance_charge_type: str = "PostPaid",
    ):
        super().__init__(
            region_id=region_id,
            resource_group_id=resource_group_id,
            security_group_id=security_group_id,
            zone_id=zone_id,
            v_switch_id=v_switch_id,
        )

        # most important parameters
        self.instance_name = instance_name
        self.instance_type = instance_type
        self.system_disk_size = system_disk_size
        self.data_disk_size = data_disk_size
        self.image_id = image_id

        # optional parameters
        self.internet_max_bandwidth_out = internet_max_bandwidth_out
        self.internet_max_bandwidth_in = internet_max_bandwidth_in
        self.password = password
        self.system_disk_category = system_disk_category
        self.data_disk_category = data_disk_category
        self.instance_charge_type = instance_charge_type

    @retry_decorator()
    @rate_limit()
    async def create_instances_async(self, amount: int = 1) -> List[str] | None:
        return await super().create_instances_async(
            amount=amount,
            instance_name=self.instance_name,
            instance_type=self.instance_type,
            system_disk_size=self.system_disk_size,
            data_disk_size=self.data_disk_size,
            image_id=self.image_id,
            internet_max_bandwidth_out=self.internet_max_bandwidth_out,
            internet_max_bandwidth_in=self.internet_max_bandwidth_in,
            password=self.password,
            system_disk_category=self.system_disk_category,
            data_disk_category=self.data_disk_category,
            instance_charge_type=self.instance_charge_type,
        )

    @retry_decorator()
    @rate_limit()
    async def delete_instance_async(self, instance_id: str | List[str], region_id: str = None) -> Dict[str, Any] | None:
        print(f"Deleting instance: {instance_id}")
        return await super().delete_instance_async(instance_id)

    @retry_decorator()
    @rate_limit()
    async def attach_disk_async(
        self,
        disk_id: str,
        instance_id: str = None,
        delete_with_instance: bool = False,
    ) -> ecs_20140526_models.AttachDiskResponseBody | None:
        return await super().attach_disk_async(
            disk_id,
            instance_id or self.instance_id,
            delete_with_instance,
        )
