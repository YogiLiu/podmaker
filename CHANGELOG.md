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
