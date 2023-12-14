from typing import Literal

from dataclasses import dataclass

# local imports
from rag.configs.singleton import SingletonMeta, SingletonCalledBeforeDefinedError

RequiredEnvVars = Literal[
    'TRANSCRIPTS_DOWNLOAD_DIR',
    'PINECONE_KEY',
    'PINECONE_INDEX_NAME',
    'PINECONE_ENVIRONMENT',
    'OPENAI_API_KEY'
]



################# NOT BEING USED ATM, when used will need to reflect RequiredEnvVars literals always, so updated alongside it
'''
# NOTE: to switch from `load_dotenv() & os.getenv()` - this gets constructed 
in EnvVarSetupCLI & is a Singleton object which gets imported where keys are
needed (it inherits from a Singleton Metaclass to prohibit further instances)
'''
@dataclass 
class EnvVarsHolder(metaclass=SingletonMeta):
    TRANSCRIPTS_DOWNLOAD_DIR: str = NotImplemented
    PINECONE_KEY: str = NotImplemented
    PINECONE_INDEX_NAME: str = NotImplemented
    PINECONE_ENVIRONMENT: str = NotImplemented
    OPENAI_API_KEY: str = NotImplemented

    def __post_init__(self):
        '''
        Automatic actions taken post initialisation,
        '''
        if any([_prop is NotImplemented
            for _prop in (
                self.TRANSCRIPTS_DOWNLOAD_DIR,
                self.PINECONE_KEY,
                self.PINECONE_ENVIRONMENT,
                self.PINECONE_INDEX_NAME,
                self.OPENAI_API_KEY
            )
        ]):
            raise SingletonCalledBeforeDefinedError()