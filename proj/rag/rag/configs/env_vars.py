import os
import argparse
from dataclasses import dataclass
from dotenv import load_dotenv

from typing import Literal, get_args

# local imports
from rag import module_path
from rag.configs.singleton import SingletonMeta, SingletonCalledBeforeDefinedError

ENV_PATH = f'{module_path}/.env'

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

##########################################################
# NOTE: main env_var trigger function

def set_env_vars():
    if os.path.exists(ENV_PATH):
        env_var_file = open(ENV_PATH, 'r+')
        env_var_str = env_var_file.read()
    else:
        env_var_file = open(ENV_PATH, 'a+')
        env_var_str = ''
    required_vars = get_args(RequiredEnvVars)
    for var in required_vars:
        if var not in env_var_str:
            key = input(f'Please enter your key or path for {var}: ')
            line = f'{var} = "{key.strip()}"\n'
            env_var_file.write(line)
    env_var_file.close()
    lines = '\t\t'.join(open(ENV_PATH, 'r').readlines())
    load_dotenv(override=True)
    print(f'''
    Your env vars have loaded succesfully, for verification they are as so:\n
    \t{lines}

    If you need to manually edit them then please find the `.env` file located at:
    \t`{ENV_PATH}`
    ...but don't change the key names just the values
    ''')

if __name__ == "__main__":
    set_env_vars()