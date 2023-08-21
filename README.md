# Podmaker

Convert online media into podcast feeds.

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
The example configuration file is [config.example.toml](config.example.toml).

## Usage

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
    - [ ] Channel
- [ ] BiliBili

### Resource Hosting

- [x] S3

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

See [LICENSE](LICENSE).