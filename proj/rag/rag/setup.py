import os
import argparse
from dotenv import load_dotenv

from typing import get_args

# local imports
from rag import module_path
from rag.configs.env_vars import EnvVarsHolder, RequiredEnvVars
from rag.configs.rag_settings import load_rag_settings_objects


class EnvVarSetupClient:

    ENV_PATH = f'{module_path}/.env'

    def __init__(self):
        if os.path.exists(self.ENV_PATH):
            env_var_file = open(self.ENV_PATH, 'r+')
            env_var_str = env_var_file.read()
        else:
            env_var_file = open(self.ENV_PATH, 'a+')
            env_var_str = ''
        required_vars = get_args(RequiredEnvVars)
        for var in required_vars:
            if var not in env_var_str:
                key = input(f'Please enter your {var}: ')
                line = f'{var} = "{key.strip()}"\n'
                env_var_file.write(line)
        env_var_file.close()
        lines = '\t\t'.join(open(self.ENV_PATH, 'r').readlines())
        load_dotenv(override=True)
        print(f'''
        Your env vars have loaded succesfully, for verification they are as so:\n
        \t{lines}

        If you need to manually edit them then please find the `.env` file located at:
        \t`{self.ENV_PATH}`
        ...but don't change the key names just the values
        ''')


if __name__ == '__main__':
    EnvVarSetupClient()
    load_rag_settings_objects() # the singleton hosting all settings (api/model config for pinecone etc.), accessible via. `import SettingsHolder`
    pass