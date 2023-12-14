# Installation
0. make sure you have (`python`)[https://www.python.org/downloads/] installed - the version must be greater than `3.8`

1. package dependencies via. (`poetry`)[https://python-poetry.org/docs/]
    - install via. instructions on website, i used `curl -sSL https://install.python-poetry.org | python3 -`
        - follow the install page for any troubleshooting
    - inside this root folder `rag` execute `poetry install`
        - it will install the pkgs from the `pyproject.toml`
        - you can add new packages via. `poetry add {pkg}`
    - enter your virtual env by executing `poetry shell`
        - this has all your dependencies available
        - you may need to play around to associate this with your IDE (such as (`VSCode`)[https://code.visualstudio.com/docs/python/environments#_working-with-python-interpreters])
        - you can find the path to your virtual env interpreter using `poetry env list --full-path`
    - after initial setup:
        - whenever you pull from github execute `poetry install` or `poetry update` in case the `pyproject.toml` has changed
        - remember you are only in the virtual env after running `poetry shell`
            - the .venv files will then live inside the folder you ran the `poetry install` in
            - you can remove any envs using `poetry env remove {path|env-name}`
            - you can exit your virtual env using `deactivate`

2. downloading the transcription data from google-drive
    - download the data from https://drive.google.com/drive/folders/0AL0-_RLA7pqDUk9PVA - if you don't have access ask Sam or Darin
    - create a folder outside of the `TWIML-RAG` repo (so your data download doesn't get uploaded to github when pushing) & remember the full path of the folder with the data in it eg. `/home/<username>/twiml-transcripts`

3. setting up your `.env` file with necessary keys for apis & cloud services
    - sign up to the openai api, or ask Sam for the shared projects' openai api key if there is one
    - sign up to pinecone, or ask for the shared projects' pinecone api key if there is one
    - run `python rag/setup.py` from within the top-level `rag` folder i.e. where this README is
        - enter your keys as prompted, and if you need to edit them change your local `.env`
        - if you need to add new keys to the process add them to the `RequiredEnvVars` type in `rag/rag/configs/env_vars.py` 

4. getting your pinecone index set up (dimensions etc.)
