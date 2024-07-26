import os
from functools import lru_cache
from dotenv import load_dotenv


class Config:
    PREFIX = "staging"
    BASE_DIR = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))


class StagingConfig(Config):
    PREFIX = "staging"


class ProductionConfig(Config):
    PREFIX = "prod"


@lru_cache()
def get_settings():
    config_cls_dict = {
        'staging': StagingConfig,
        'production': ProductionConfig
    }
    env_dict = {
        'staging': '.env.staging',
        'production': '.env.prod'
    }

    config_name = 'staging'
    config_cls = config_cls_dict.get(config_name)
    env_path = os.path.join(Config.BASE_DIR, env_dict.get(config_name))
    load_dotenv(env_path)
    config_instance = config_cls()

    return config_instance


settings = get_settings()
