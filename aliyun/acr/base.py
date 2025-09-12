import os
from typing import List

from alibabacloud_cr20181201 import models as cr_20181201_models
from alibabacloud_cr20181201.client import Client as cr20181201Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models


class AcrClient:

    def __init__(self, region_id: str):
        """
        Initialize the ACR client
        """

        self.region_id = region_id
        self.client = self.create_client()

    def create_client(self) -> cr20181201Client:
        """
        Create the ACR client
        """

        config = open_api_models.Config(
            access_key_id=os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
            access_key_secret=os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'],
        )
        config.endpoint = f'cr.{self.region_id}.aliyuncs.com'
        return cr20181201Client(config)

    async def list_images_async(self, instance_id: str, repo_id: str, page_size: int = 200) -> List[str]:
        """
        List all images in a repository
        """
        runtime = util_models.RuntimeOptions()
        page_no, tags = 1, []
        while True:
            list_repo_tag_request = cr_20181201_models.ListRepoTagRequest(
                instance_id=instance_id,
                repo_id=repo_id,
                page_size=page_size,
                page_no=page_no,
            )
            response = await self.client.list_repo_tag_with_options_async(list_repo_tag_request, runtime)
            tags.extend([image.tag for image in response.body.images])
            if len(response.body.images) < page_size:
                break
            page_no += 1
        return tags
