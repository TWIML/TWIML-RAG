import tomllib
from dataclasses import dataclass
from typing import Any, Dict, Literal, get_args

# local imports
from rag import src_path
from rag.configs.singleton import SingletonMeta, SingletonCalledBeforeDefinedError

ExpectedSettingsSections = Literal[
    'pinecone-embeddings',
    'openai-conversation',
    'streamlit-application'
]


# NOTE: you probably want to add protocols mirroring the dataclasses just for type enforcing & hinting etc.

@dataclass
class PineconeSettings:
    EMBEDDING_MODEL: str # the model used to embed transcripts & queries for the rag-step - which retrieves relevant docs to pass to the llm chatbot as grounding context
    EMBEDDING_DIMENSIONS: int # the number of dimensions of the embedding - ensure your index is set with this dimension too

@dataclass
class OpenAiSettings:
    VECTOR_TOP_P: int # NOTE: understand and make comment on what this does

@dataclass
class StreamlitSettings:
    MEMORY_K: int # NOTE: understand and make comment on what this does

@dataclass
class SettingsHolder(metaclass=SingletonMeta):
    Pinecone: PineconeSettings = NotImplemented
    OpenAi: OpenAiSettings = NotImplemented
    Streamlit: StreamlitSettings = NotImplemented

    def __post_init__(self):
        '''
        Automatic actions taken post initialisation,
        '''
        if any([_prop is NotImplemented
            for _prop in (
                self.Pinecone,
                self.OpenAi,
                self.Streamlit
            )
        ]):
            raise SingletonCalledBeforeDefinedError()


def load_settings_objects(config_path=f'{src_path}/settings.toml') -> SettingsHolder:
    '''
    Loads settings from `settings.toml`, related to api's etc. - called on `setup.py`
    '''
    with open(config_path, 'rb') as fh:
        config = tomllib.load(fh)
    if set(config.keys()) == set(get_args(ExpectedSettingsSections)):
        pinecone_config = config['pinecone-embeddings']
        openai_config = config['openai-conversation']
        streamlit_config = config['streamlit-application']
        print("Your settings are being loaded (for pinecone, openai etc.)")
        return SettingsHolder(
            Pinecone=PineconeSettings(**pinecone_config),
            OpenAi=OpenAiSettings(**openai_config),
            Streamlit=StreamlitSettings(**streamlit_config)
        )
    else:
        raise Exception(f'''
        It seems there is a mismatch between the sections expected from
        the `src/config.toml` and the sections in there at present
        
        Please ensure alignment between the two by adding any new sections
        to the ExpectedConfigSection type in {__file__}, or removing any
        redundant sections
        ''')
    
if __name__ == "__main__":
    load_settings_objects()