import os

ZONE_ID_TO_V_SWITCH_ID = {
    "cn-shanghai-b": os.getenv("VSWITCH_ID_CN_SHANGHAI_B"),
    "cn-shanghai-e": os.getenv("VSWITCH_ID_CN_SHANGHAI_E"),
    "cn-hongkong-b": os.getenv("VSWITCH_ID_CN_HONGKONG_B"),
    "ap-southeast-1a": os.getenv("VSWITCH_ID_AP_SOUTHEAST_1A"),
    "ap-southeast-1b": os.getenv("VSWITCH_ID_AP_SOUTHEAST_1B"),
    "ap-southeast-1c": os.getenv("VSWITCH_ID_AP_SOUTHEAST_1C"),
}

REGION_ID_TO_SECURITY_GROUP_ID = {
    "cn-shanghai": os.getenv("SECURITY_GROUP_ID_CN_SHANGHAI"),
    "cn-hongkong": os.getenv("SECURITY_GROUP_ID_CN_HONGKONG"),
    "ap-southeast-1": os.getenv("SECURITY_GROUP_ID_AP_SOUTHEAST_1"),
}

IMAGES_MAP = {
    "ubuntu-22.04": "ubuntu_22_04_x64_20G_alibase_20250324.vhd",
}
