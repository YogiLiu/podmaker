## 0.7.4 (2023-08-27)

### Fix

- **rss.podcast**: fix pu_bdate format
- **fetcher.processor**: check exit signal

## 0.7.3 (2023-08-26)

### Fix

- **config**: fix tomlkit

## 0.7.2 (2023-08-26)

### Fix

- **config.core**: fix union

## 0.7.1 (2023-08-26)

### Fix

- **config.storage**: remove absmeta

## 0.7.0 (2023-08-25)

### Feat

- **storage**: support local storage

### Fix

- **cli**: support local storage
- **rss.podcast**: fix items merge
- **fetcher.youtube**: add source id to skip log

## 0.6.1 (2023-08-25)

### Fix

- **fetcher.youtube**: cache dir

## 0.6.0 (2023-08-25)

### Feat

- **fetcher.youtube**: add source id to log

## 0.5.0 (2023-08-25)

### Feat

- **storage**: support start and stop storage
- **config**: support filter episodes by regex
- **config**: use storage instead s3

## 0.4.0 (2023-08-24)

### Feat

- **fetcher**: support youtube channel

### Fix

- **rss.core**: remove stylesheet
- **fetcher.youtube**: catch download error
- **rss.podcast**: fix image url

## 0.3.1 (2023-08-23)

### Fix

- **peocessor.task**: fix mime
- **asset**: fix script url

## 0.3.0 (2023-08-23)

### BREAKING CHANGE

- changes for config file

### Feat

- **rss**: add stylesheet
- add exit signal

### Fix

- **rss.core**: fix encoding of rss bytes
- **config**: change s3.cdn_prefix to s3.public_endpoint

### Refactor

- **processor**: move execution to Task class, and support task hook

## 0.2.2 (2023-08-22)

### Fix

- **fetcher.youtube**: fetch image and link for episode

## 0.2.1 (2023-08-21)

### Fix

- **config**: quote id before used to generate storage key

## 0.2.0 (2023-08-21)

### Feat

- add cli
- **processor**: add processor
- **rss**: support mergation
- **rss**: use qname to manage namespace
- **rss**: support load rss object from xml string
- **rss.core**: add plain resource and rss deserializer
- **config**: add source config
- **config**: support optional env and required env
- add config
- **rss**: add rss generator and serializer
- complete youtube parser and s3 storage

### Fix

- **rss**: compatible with apple's requirements
- **processor.scheduling**: add next run time to add_job
- **config**: fix decorator
- **config**: fix tomlkit
- **processor.scheduling**: fix shutdown
- **fetcher.youtube**: fix logger
- **config**: rename source.name to source.id
- **processor.schedulling**: fix shutdown
- **processor.core**: fix rss key
- **rss**: fix text
- **config**: add app config
- **processor.core**: fix original file
- change cli argument
- **fetcher.youtube**: add lock
- **fetcher**: rename parser to fetcher
- **parser.youtube,-storage.s3**: remove redundant config dependency
- **rss**: reduce public class
- **env**: use dataclass as env object
- **rss.podcast**: fix category pattern
- supplement podcast field

### Refactor

- **cli**: remove cli logic to cli module
- add log
- **rss**: hide unnecessary property
- **parser.youtube**: use lru_cache
- **config**: rename env to config and use pydantic manage config
