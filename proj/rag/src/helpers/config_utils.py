import tomllib
from dataclasses import dataclass
from typing import Any, Dict, Literal, get_args

# local imports
from src import src_path

ExpectedSettingsSections = Literal[
    'pinecone-embeddings',
    'openai-conversation'
]


# NOTE: you probably want to add protocols mirroring
# the dataclasses just for type hinting etc.

@dataclass
class PineconeSettings:
    EMBEDDING_MODEL: str

@dataclass
class OpenAiSettings:
    VECTOR_TOP_P: int
    MEMORY_K: int


def load_settings_objects(config_path=f'{src_path}/settings.toml') -> Dict[ExpectedSettingsSections, Any]:
    with open(config_path, 'rb') as fh:
        config = tomllib.load(fh)
    if set(config.keys()) == set(get_args(ExpectedSettingsSections)):
        pinecone_config = config['pinecone-embeddings']
        openai_config = config['openai-conversation']
        return {
            'pinecone-embeddings': PineconeSettings(**pinecone_config),
            'openai-conversation': OpenAiSettings(**openai_config)
        } # index return as `pinecone_cfg = config_objects['pinecone-embeddings']`
    else:
        raise Exception(f'''
        It seems there is a mismatch between the sections expected from
        the `src/config.toml` and the sections in there at present
        
        Please ensure alignment between the two by adding any new sections
        to the ExpectedConfigSection type in {__file__}, or removing any
        redundant sections
        ''')