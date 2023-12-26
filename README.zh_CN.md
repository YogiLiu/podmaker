# Podmaker

*本文档的其他语言: [English](README.md), [简体中文](README.zh_CN.md)*

将在线媒体转换成播客订阅。

![PyPI - Version](https://img.shields.io/pypi/v/podmaker)
![PyPI - Status](https://img.shields.io/pypi/status/podmaker)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/podmaker)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/podmaker)
![PyPI - License](https://img.shields.io/pypi/l/podmaker)


## 功能

- 从网络视频中提取音频；
- 无需额外部署 Web 服务；
- 自动生成播客订阅；
- 通过 `watch` 模式自动更新订阅。

## 依赖

本工具使用 **ffmpeg** 从视频中提取音频，请确保 `$PATH` 中包含 `ffmpeg`。

另外, 你可以更根据你的需求安装额外的依赖：

- `podmaker[all]`: 安装下述的所有依赖；
- `podmaker[s3]`: 提供 S3 支持；
- `podmaker[youtube]`: 提供 YouTube 支持。

你可以使用 `podmaker[extra1,extra2,...]` 的方式同时安装多个额外依赖。

## 配置

在开始使用本工具之前，请先准备一个 TOML 格式的配置文件。
默认情况下，配置文件位于 `${WORK_DIR}/config.toml`。你可以通过 `-c` 或 `--config` 选项来指定配置文件的路径。
你可以在 [config.example.toml](https://github.com/YogiLiu/podmaker/blob/main/config.example.toml) 中找到一个示例配置文件。

## 使用方法

### Systemd

使用 systemd 后台运行本工具（需要 root 权限）：

```bash
# 创建虚拟环境
apt install python3 python3-venv
mkdir -p /opt/podmaker && cd /opt/podmaker
python3 -m venv venv

# 安装 podmaker
./venv/bin/pip install "podmaker[all]"

# 创建配置文件
curl -o config.toml https://raw.githubusercontent.com/YogiLiu/podmaker/main/config.example.toml
vim config.toml

# 创建 systemd 服务
curl -o /etc/systemd/system/podmaker.service https://raw.githubusercontent.com/YogiLiu/podmaker/main/systemd/podmaker.service
systemctl daemon-reload

# 启动服务，并设置开机自启
systemctl enable podmaker
systemctl start podmaker
```

### 手动运行

### 使用 pip 安装

为了获得最佳体验，我们建议你在虚拟环境中安装本工具。

```bash
pip install "podmaker[all]"
```

### 使用 `pipx` 安装

```bash
pipx install "podmaker[all]"
```

### 运行

```bash
podmaker -c path/to/config.toml
```

或者 
    
```bash
python -m podmaker -c path/to/config.toml
```

## 项目规划

### 平台支持

- [x] YouTube
    - [x] 播放列表
    - [x] 频道
- [ ] 哔哩哔哩（鸽）

### 资源托管

- [x] S3
- [x] 本地文件

## 贡献指南

你的贡献弥足珍贵，请不要吝啬提出你的 Pull Request。
在提交代码之前，请确保你的代码通过单元测试和 `autohooks`。

你可以使用下述命令激活 `autohooks`：

```bash
poetry run autohooks activate --mode poetry
```

这个程序会自动进行代码风格检查、格式化和 import 排序。

如果你添加了新的功能，请确保提供了相应的测试。

## 许可证

查看许可证详情，请参阅 [LICENSE](https://github.com/YogiLiu/podmaker/blob/main/LICENSE)。