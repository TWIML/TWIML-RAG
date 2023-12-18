
def step_1():
    '''
    All the setup steps for codebase architecture and env etc.

    NOTE: motivated as a hacky workaround to avoid singleton being 
    called before definition, now also returns any init objects so
    that the can be passed around
    '''
    from rag.configs.env_vars import set_env_vars
    from rag.configs.rag_settings import load_settings_objects
    set_env_vars()
    load_settings_objects()

def step_2():
    '''
    The rest of the setup - api's etc.
    '''
    from rag.helpers.pinecone_indexes import run_pinecone_setup
    run_pinecone_setup()

def run_setup():
    step_1()
    step_2()

if __name__ == '__main__':
    run_setup()