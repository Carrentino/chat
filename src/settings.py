from functools import lru_cache

from fastapi_storages import S3Storage
from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    url: str = Field(default='redis://localhost:6379')

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        str_strip_whitespace=True,
        validate_default=True,
        case_sensitive=False,
        extra='ignore',
        env_prefix='redis_',
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        str_strip_whitespace=True,
        validate_default=True,
        case_sensitive=False,
        extra='ignore',
    )

    host: str = '127.0.0.1'
    port: int = 8080
    workers_count: int = 1
    reload: bool = True

    log_level: str = Field(default='info')
    debug: bool = True
    debug_postgres: bool = False

    environment: str = 'dev'

    postgres_dsn: PostgresDsn = Field(  # type: ignore
        default='postgresql+asyncpg://postgres:postgres@localhost:5432/base'
    )
    test_postgres_dsn: PostgresDsn = Field(  # type: ignore
        default='postgresql+asyncpg://postgres:@localhost:5432/base_test'
    )

    trace_id_header: str = 'X-Trace-Id'
    jwt_key: SecretStr = Field(default=SecretStr('551b8ef09b5e43ddcc45461f854a89b83b9277c6e578f750bf5a6bc3f06d8c08'))
    aws_access_key_id: str = Field(default='minio', validation_alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default='miniominio', validation_alias="AWS_SECRET_ACCESS_KEY")
    aws_s3_bucket_name: str = Field(default='local-bucket', validation_alias="S3_BUCKET_NAME")
    aws_s3_endpoint_url: str = Field(default='localhost:9000', validation_alias="S3_ENDPOINT_URL")
    aws_s3_use_ssl: bool = Field(default=False)
    redis: RedisSettings = RedisSettings()

    @property
    def storage(self):
        class S3CustomStorage(S3Storage):
            AWS_ACCESS_KEY_ID = self.aws_access_key_id
            AWS_SECRET_ACCESS_KEY = self.aws_secret_access_key
            AWS_S3_BUCKET_NAME = self.aws_s3_bucket_name
            AWS_S3_ENDPOINT_URL = self.aws_s3_endpoint_url
            AWS_S3_USE_SSL = self.aws_s3_use_ssl

        return S3CustomStorage()


@lru_cache
def get_settings() -> Settings:
    return Settings()
