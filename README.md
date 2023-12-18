# Description & TOC
*to be written*

# Tasks & next-steps
*next steps for extending the codebase & tasklists to select from (or add to for people to pick up work from, get ideas etc.) - to be written*

- [ ] Polish up pinecone setup step (Uploading of documents to pinecone indexes is not currently being done by script - run `nbs/Pinecone_Indexing.ipynb` for now!)
    - Don't process and chunk docs that have already been done (keep some static record, json etc. locally) & write chunks (w. some id or primary key) to the transcripts dir, and ingest from there, for now
    - Don't upload docs to pinecone index which are already there, maybe assign metadata to them with an id/hash of the podcast name and pull down that list and only load docs that are not in it (maybe there's a nicer way via. langchain api)
- [ ] Transferring all setup, config functionality to UI from CLI
    - including keys, settings, file loading, api access etc. (everything except the `poetry` installation)
    - might be worth moving from `load_dotenv` as `.env` files are not git tracked so the user may have to enter them in each time they pull, best to store the keys outside repo and use a class interface to store it at same relative location and pull in
- [ ] Streamlit UI components and extensible front-page (tabs for new/separate dev pages etc.)
    - to enable components to be grouped and new pages to be easily added for prompt tuning & document embedding explorations etc. - basically enabling extensibility and separate pages per dev/exploration to be picked up automatically by the interface
    - enable feedback mechanisms so people can rank/rate prompts for particular intents & create ways to organise and store prompts
    - create model experimentation and tracking space (for embeddings in particular) - to evaluate retrieval
- [ ] Codebase structure and architecture
    - Class interfaces for streamlit app components/wrappers, for pinecone/openai api, for common langchain tasks etc. and esp. for interactions around codebase - passing keys, settings, responses, writing to files, collecting user input from ui and storing, cacheing, running access tests for api-accounts etc.
          - & eventually for pulling in/connecting to transcription pipeline and gcp services (or other cloud)
    - Then create diagram for codebase interfaces and the overall solution architecture (inc. transcription pipeline & infra etc.)


# Running the app locally
`streamlit run rag/app.py --server.headless true`
    - then copy the server-ip and paste in your browser

# Installation and initial setup (for devs)
0. make sure you have (`python`)[https://www.python.org/downloads/] installed - the version must be greater than `3.8`

1. package dependencies via. (`poetry`)[https://python-poetry.org/docs/]
    - install via. instructions on website, i used `curl -sSL https://install.python-poetry.org | python3 -`
        - follow the install page for any troubleshooting
    - inside this root w. the `pyproject.toml` execute `poetry install`
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
    - download the data from (GOOGLE-DRIVE)[https://drive.google.com/drive/folders/0AL0-_RLA7pqDUk9PVA] - if you don't have access ask Sam or Darin
    - create a folder outside of the `TWIML-RAG` repo (so your data download doesn't get uploaded to github when pushing) & remember the full path of the folder with the data in it eg. `/home/<username>/twiml-transcripts`
    - place your downloaded data in this folder and copy the path to enter later

3. setting up your `.env` file with necessary keys for apis & cloud services
    - sign up to the openai api, or ask Sam for the shared projects' openai api key if there is one
    - sign up to pinecone, or ask for the shared projects' pinecone api key if there is one
    - run `python rag/setup.py` or `streamlit run rag/app.py` from within the top-level `rag` folder i.e. where this README is
        - enter your keys as prompted in the cli, and if you need to edit them change your local `.env`
            - best to keep a copy of this as it is not tracked by git (same for the pkgs installed in `.venv`) so if you switch branch etc. or pull they will disappear I believe
        - if you need to add new keys to the process add them to the `RequiredEnvVars` type in `rag/configs/env_vars.py` 

4. getting your pinecone index set up (dimensions etc.)
    - you must create a pinecone account and note the variables referring to it (key and project environment), the setup script should do the rest for you such as create an index if one under the name you entered does not exist etc.
    - IT DOES NOT CURRENTLY DO THE LOADING - TBD

# App user features and interactivity
*sections of the app, features for the user and how they might interact w. podcasts and learn ml etc. - to be written*

# Codebase architecture and solution design
*the folder structure, class interfaces etc. and how this folder/repo integrates with the overall solution (cloud services & pipeline) - to be written*

# Model evaluation and comparison
*model comparison tables, evaluation metrics and links - to be written*

# Prompt ideas and discussion
*standard prompts for different aspects and requirements of the rag and user interaction - to be written*

# Background to RAG & LLM operation
*explanations of how RAG & LLM's work and the libs, tools and apis used for them such as vector dbs, model apis, chat-gpt etc. - to be written*

# How to contribute
*how a dev can contribute to the project - to be written*
