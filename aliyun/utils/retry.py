import os

from tenacity import retry, retry_if_result, stop_after_attempt, wait_fixed

ALIYUN_API_MAX_RETRIES = int(os.environ.get("ALIYUN_API_MAX_RETRIES", 5))
ALIYUN_API_RETRY_DELAY = int(os.environ.get("ALIYUN_API_RETRY_DELAY", 5))


def retry_decorator(
    max_retries: int = ALIYUN_API_MAX_RETRIES,
    retry_delay: int = ALIYUN_API_RETRY_DELAY,
):
    return retry(
        retry=retry_if_result(lambda x: x is None),
        stop=stop_after_attempt(max_retries),
        wait=wait_fixed(wait=retry_delay),
        reraise=True,
    )
