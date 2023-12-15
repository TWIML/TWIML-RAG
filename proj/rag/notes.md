# How to proceed (simple steps, keeping things as close to they are as of now & incrementally tweaking)
1. setting up pinecone index (& conditional loading)
...
*. executing tests on the api's (pinecone, openai etc.) - to ensure connectivity
*. finishing up README.md & check everything works
    - repeat till finished

# Install instructions for `rag` folder
- folder setup (& manual data download into it for now)
- keys & env-vars (signing up to api's or asking @sam)
- package dependencies (just for `rag` folder for now)
- setup script (eg. `setup.py` for now till `main.py` is sorted - enabling them to run jupyter nbs cleanly)
- running streamlit app
- etc.

# CLI setup tool for `rag` folder
- folder setup (also: put instructions for requesting google-drive access in README)
    - input prompt: `You are currently in {pwd} directory, please state the directory to use for accessing the transcripts`
    - helper prompt: `You must download the transcripts manually from google drive for now and place them in this folder`
    - info prompt: `You have {x} number of files in the directory, here is a sample of {y} random files`
    - notes: 
        - only prompt if they have not already set a directory 
        - store any directory they enter into `.env` and check settings from there
        - store the files in the subfolder they state for the data eg. if they say dir `x` - (`x/data/transcripts/`)
        ~ (maybe, after the rest) also set an `.env` var for the `nltk-data` directory
            - write a function to pull the nltk-data there

- keys & env-vars (also: put instructions for sign-ups in README)
    - input prompt: `Would you like to set-up your env vars from the CLI (y/n)`
        - if `y` then take them through the flow using `arparse` library and `input` prompts
        - if `n` then print a message
            - helper prompt: `You must set up your own `.env` file within the root dir of this folder - {pwd}, it must contain the following keys {list of env-var names expected}`
    - helper prompt: `Your keys are now located in {pwd/.env}, they should not be pushed to git, please verify so from the .gitignore`
    - notes:
        - only prompt if they have not already got a .env file
            - if they do have one with all necessary env-var:key pairs skip the prompts
            - if they do but missing certain env-var:key pairs then prompt for only those
                - keep a Literals data-structure to help with this (do the simplest thing)
        - print their keys to screen for verification from them if they went through any CLI prompts to setup
            - simple plain print for now, maybe hash out parts later (for some safety, in case demoing to someone)

- package dependencies (also: put poetry install instructions in README)
    - use poetry for package dependencies, just for the `rag` folder for now & discuss using it at module level
    - state the commands to use for 
        - accessing poetry env eg. `poetry shell` 
        - adding new libs - `poetry add {pkg}`
        - installing libsl - `poetry install`
            - &... 
            - mention benefits of tying to version, setting up linting config etc. 
            - try to help w. troubleshooting info

- try out streamlit app (just to check everything works)
        

# Extensions of CLI setup & DevOps-y stuff
- writing `pytest` for api-connectivity before proceeding with confirming setup 
    - eg. dummy api-call or access-test etc. w/ printout of account name, plan or so on
- adding `mypy` type-hinting and solidifying interfaces, custom types (protocols), and linting etc. (via. the `pyproject.toml`)
- polishing `pyproject.toml` for adding readme, repository, version tying, module etc. (docs)[https://python-poetry.org/docs/pyproject/]
- relative file imports will be dangerous down the line, best to have single repo with main module entry point and name, which self installs in poetry, and is linked to a repo, and always reference from the src of repository
    - if it needs any other repos written by devs working on the overall project then that can be added to `pyproject.toml` w. repo url and can be installed like that, can also link to a version of it only (using tags and version tagging for a specific commit - check github options)
- setup github actions for tests, linting etc.

-----------------------------------------

# Possible Architecture
- removing the folder levels, and keeping main src at top-level, with tests on same level & all set-up and config there as well - with only 1 set of config for a repo (see below)
    - having at the top-level of the repo 
        - all the pkg-dependency, git, cicd files, README etc.
        - the `tests` folder
        - the `prompts` folder - for storing prompts
        - the `src` folder - where all the functionality for class interfaces, config, helpers, connections, processing etc. lives
        - the `app` folder - where the application ui and backend functionality lives
            - maybe split up into `frontend` & `backend`
            - `backend` would handle connection to the other repos or steps in the pipeline, cloud services etc.
            - `frontend` for the user interactivity components and structure etc.
- splitting folders into separate repos, each w. their own requirements
    - `transcription-pipeline` repo: (triggered by rss/pubsub) 
        - for pulling audio files, doing speech to text, and loading transcripts to google storage
    - `rag-application` repo: (always on vm - listening for new transcripts via. webhook, and serving application) (2 folders - `app` & `rag`)
        - `rag` folder: for pulling transcripts from google storage, training rag model, & serving a final model-api (or config)
            - `exploration` subfolder: for jupyter notebooks, notes, findings etc. on rag-modelling etc.
        - `app` folder: hosting the application back & frontend for user interactivity actions & interaction with rag model
        ...alternatively these could both be separate with the `app` living on a always on server, and the `rag` being a repo for experiments, with the final model pushed to some kind of model registry with an api into it perhaps? this could also permit to have different model versions for different users (eg. payment level - free or so on), or instead of a registry could create the model-api functionality ourselves but difficult to achieve as must have to have an always on server to listen for requests and run through the model etc.
            - note for self: i may be mistaken in using the term `model` and thinking in an outdated way, the model is really just open source, we might actually just be storing config for api's and selections of embedding types etc. after having tested them, in which case the model api exists already, we just need to store our final config after experimentation, so could still have separate `rag` and `app` repos, latter for productionised web-application, former for experiments and maybe linked to some external experiment tracking eg. in `ml-flow` or `w&b` etc.


# Setup & Resource Requests
- would be good if we could have a shared `pinecone` & `open-ai` account and permit devs to use the keys, like a service account
- would be good to also have access to a shared `gcp` project with same key or separate accounts for devs
    - with access to `cloud functions`, `pubsub`, `storage` & `compute` to start with

# Notes
- what features should twiml rag have as a user application, what should the ui be like, what should they be able to do with it
    - does it have different sections for topical background (fundamentals, seminal papers, some summary of the research area etc.) for all topics the podcasts cover - could it serve as an all in one educational platform for both latest topics in ai but also the background needed
        - how could it sort and aggregate research areas, techniques and topics in a sensible manner, could it be somehow linked to user feedback to direct and guide it to tweak how it does things (similar to active learning) - eg. provide ui for user to rate it's responses and organising of topics etc. and turn those into prompts or some form of training guard-rails
    - does it have user sessions & logins, so they can store their favourite prompts, purchase credits to interact with the data more etc.
    - might it have community sections where people can submit comments and messages discussing a podcast, perhaps the transcript is presented on the ui, and like in `discus/rap-genius` or similar, you can highlight the sections and add comments and ratings on etc. for explaining their background and so forth - this could later be used as training data for the model to be contextualised with in order to supplement it's responses and conversations around certain topics

- what might the eventual architecture and platform infrastructure need to be to support the above - cloud services, codebase architecture etc.
    - what db is most appropriate for different requirements (vectors and prompts, user history and interactivity etc.)
    - what web-framework is simplest and easiest to support all the needs 
        - maybe just fast-api and a frontend, or perhaps flutter so it can be mobile flexible as well, or django-react? 
        - keeping in mind this is open-source so needs to be dev friendly for people to contribute in free time
    - what codebase architecture will enable sustainable structure, refactoring, extensions etc. & permit easy open-source collaboration
        - what key classes, interfaces, and segmentation of applications for different purposes of sections of the codebase eg.
            - cicd, infrastructure and devops aspects
            - task orchestration and data pipelines
            - backend for ui interactivity (user aspects - payments, accounts + community aspects - comments, ratings etc.)
            - frontend features (as for above - but also sections for background on ai topics, for main portal to converse over podcasts etc.)
            - task triggers for retraining or enriching with user interactivity data (comments, ratings etc.)
            - model training and experimentation etc.

- what about testing, cacheing outputs, and model experiment tracking etc.
    - can tests work with llms, can we automate more of the setup, esp. the model selection for embeddings etc.
    - is there value in storing example cached outputs of the model to be used for populating the app with templated responses etc.
    - can we use something like `mlflow` to store the results of experiments, and maybe create template jupyter-nbs to do experiments in and store the results to the model-tracking library or data structure (for holding model name, eg. results, evaluation metrics etc.)

# Questions
- how did they get the transcriber to perform speaker identification and tag their sections of speech with their name

-----------------------------------------------------------------

# Notes from meetings (building up an idea of the product)
**(from 15/12/2023)**
What they want features to be (roughly interpreted, from a partial informal discussion):
    1. metadata about the podcast
        - length, size, title, speakers
    2. nlp analysis of content (comprehension, summarisation, linkage)
        - graphing to associate podcasts, paragraph sections
            - by topic etc.
    3. search by topic and retrieve the episodes
        - and it places you in the location of transcript (paragraph)
            - where the relevant topic is being discussed
    4. evaluation of prompts and chatbot responses
        - utilising user-feedback? (active-learning style approach)
            - linear predictors/training-data from thumbs-up/down
            ...etc. to try and direct/tune responses served by
            ...ranking prompts or tweaking them (maybe automatically
            ...using llms to rephrase sentences, intent, import of
            ...statements etc. with different synonyms, or perhaps
            ...getting it to change the sentiment, or use terms w.
            ...different wider/narrow connotations/semantics etc.)
        - tools and applications to support