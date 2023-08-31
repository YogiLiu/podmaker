# Podmaker

Convert online media into podcast feeds.

![PyPI - Version](https://img.shields.io/pypi/v/podmaker)
![PyPI - Status](https://img.shields.io/pypi/status/podmaker)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/podmaker)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/podmaker)
![PyPI - License](https://img.shields.io/pypi/l/podmaker)


## Features

- Extract audio from online videos.
- No need to deploy web services.
- Generate podcast feeds.
- Deploy with watch mode to keep feeds up-to-date.

## Dependencies

This tool uses **ffmpeg** to extract audio from videos. Ensure it's installed within `$PATH` before using this tool.

Additionally, you should install extra dependencies according to your requirements:

- `podmaker[all]`: Install all extra dependencies.
- `podmaker[s3]`: Install dependencies for S3 storage.
- `podmaker[youtube]`: Install dependencies for YouTube.

Install multiple extra dependencies simultaneously using `podmaker[extra1,extra2,...]`.

## Configuration

Before diving into this tool, craft a configuration file, a TOML file to be precise.
By default, the file resides at `${WORK_DIR}/config.toml`. Customize the path using the `-c` or `--config` option.
An example configuration file can be found at [config.example.toml](https://github.com/YogiLiu/podmaker/blob/main/config.example.toml).

## Usage

### Systemd

Deploy this tool in the background with systemd (requires root privileges):

```bash
# create virtual environment
apt install python3 python3-venv
mkdir -p /opt/podmaker && cd /opt/podmaker
python3 -m venv venv
# install podmaker
./venv/bin/pip install "podmaker[all]"
# create and edit config file
curl -o config.toml https://raw.githubusercontent.com/YogiLiu/podmaker/main/config.example.toml
vim config.toml
# create systemd service
curl -o /etc/systemd/system/podmaker.service https://raw.githubusercontent.com/YogiLiu/podmaker/main/systemd/podmaker.service
systemctl daemon-reload
# enable and start service
systemctl enable podmaker
systemctl start podmaker
```

### Manual

### Using pip

For the optimal experience, we recommend installing this tool within a virtual environment.

```bash
pip install "podmaker[all]"
```

### Using `pipx`

```bash
pipx install "podmaker[all]"
```

### Run

```bash
podmaker -c path/to/config.toml
```

or 
    
```bash
python -m podmaker -c path/to/config.toml
```

## Roadmap

### Platforms

- [x] YouTube
    - [x] Playlist
    - [x] Channel
- [ ] BiliBili

### Resource Hosting

- [x] S3
- [x] Local

## Contributing

Your contributions are invaluable. Feel free to submit pull requests.
Before committing, ensure your changes pass unit tests and `autohooks`.

To activate `autohooks`, use the following command:

```bash
poetry run autohooks activate --mode poetry
```

This process will automatically lint, format, and sort code imports.

When introducing new features, remember to provide corresponding tests.

## License

For licensing details, refer to [LICENSE](https://github.com/YogiLiu/podmaker/blob/main/LICENSE).