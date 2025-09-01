# Aliyun Kit

A Python toolkit for managing Aliyun ECS and ACR resources through their Open API.

## Features

- **ECS Management**: Create, manage, and monitor Elastic Compute Service instances
- **ACR Management**: Manage Aliyun Container Registry resources
- **Async Support**: Built with asyncio for high-performance operations
- **Rate Limiting**: Built-in rate limiting and retry mechanisms
- **Modern Python**: Requires Python 3.10+ with type hints support

## Installation

### Prerequisites

- Python 3.10 or higher
- uv package manager (recommended) or pip

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/hambaobao/aliyun-kit.git
cd aliyun-kit

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux

# Install in development mode
uv pip install -e .
```

### Using pip

```bash
pip install git+https://github.com/hambaobao/aliyun-kit.git
```

## Configuration

Set up your Aliyun credentials using environment variables:

```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="your_access_key_id"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="your_access_key_secret"
export ALIBABA_CLOUD_REGION_ID="cn-hangzhou"
```

Or create a `.env` file:

```env
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
ALIBABA_CLOUD_REGION_ID=cn-hangzhou
```

## Usage

### ECS Management

```python
from aliyun.ecs.instance import ECSInstance

# Create ECS instance
instance = ECSInstance()
await instance.create(
    instance_type="ecs.g6.large",
    image_id="ubuntu_20_04_64_20G_alibase_20200914.vhd",
    security_group_id="sg-xxx"
)
```

### ACR Management

```python
from aliyun.acr.base import ACRBase

# Manage container registry
acr = ACRBase()
repositories = await acr.list_repositories()
```


## Dependencies

- **python-dotenv**: Environment variable management
- **alibabacloud-ecs20140526**: Aliyun ECS API client
- **alibabacloud-cr20181201**: Aliyun Container Registry API client
- **tenacity**: Retry mechanism for API calls
- **aiolimiter**: Rate limiting for async operations

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please open an issue on GitHub or contact the maintainers.
