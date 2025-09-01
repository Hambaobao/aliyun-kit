from aliyun.acr.base import AcrClient
from aliyun.ecs.base import EcsClient
from aliyun.ecs.instance import EcsInstance

__all__ = ["AcrClient", "EcsClient", "EcsInstance"]

IMAGES_MAP = {
    "ubuntu-22.04": "ubuntu_22_04_x64_20G_alibase_20250324.vhd",
}
