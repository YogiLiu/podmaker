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
- Run in watch mode to keep feeds up-to-date.

## Dependencies

This project uses **ffmpeg** to extract audio from videos. Please install it before using this project.

## Installation

### Using pip

We recommend installing this project in a virtual environment.

```bash
pip install podmaker
```

### Using `pipx`

```bash
pipx install podmaker
```

## Configuration

You must create a configuration file before using this project.
The configuration file is a TOML file.
The default path is `${WORK_DIR}/config.toml`. You can use the `-c` or `--config` option to specify a different path.
The example configuration file is [config.example.toml](https://github.com/YogiLiu/podmaker/blob/main/config.example.toml).

## Usage

### Systemd

You can use systemd to run this project in the background.
The steps are as follows (need root):

```bash
# create virtual environment
apt install python3 python3-venv
mkdir -p /opt/podmaker && cd /opt/podmaker
python3 -m venv venv
# install podmaker
./venv/bin/pip install podmaker
# create config file and edit it
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

Pull requests are welcome. 
Before committing, please ensure that you have pass the unit tests and activate the `autohooks`.

You can activate the `autohooks` using the following command:

```bash
poetry run autohooks activate --mode poetry
```

It will automatically lint, format, and sort imports for the code.

If you add new features, please add tests for them.

## License

See [LICENSE](https://github.com/YogiLiu/podmaker/blob/main/LICENSE).