
## Repo Setup Instructions

There are 3 components to the repo. The first is the `speach_to_text`  which is used to create the transcripts from the podcasts and then create the embeddings from the transcripts. The second is the `azure_functions` which is used to run the azure functions locally that server as end-points for the RAG. The third is the `web_rag` which is the website to run the RAG model to call the azure end-points.

### Speech to Text Pipeline

TODO: Add instructions for the speech to text pipeline

### Qdrant Embeddings

We will use local qdrant for storing embeddings. Here we assume that we have the transcripts and the speaker information. 

We will use the BGE embeddings to create the embeddings and store them in qdrant.

1. Setup the qdrant docker image. Instructions are here: https://qdrant.tech/documentation/quick-start/
Basically just do the following (in a new directory where you want to store the qdrant data) and qdrant should be running. The run command will create and populate the 'qdrant_storage' directory automatically.
   ```
   docker pull qdrant/qdrant
   docker run -p 6333:6333 -p 6334:6334  -v $(pwd)/qdrant_storage:/qdrant/storage:z     qdrant/qdrant
   ```
   You can access the dashboard on the local qdrant on http://localhost:6333/dashboard

1. Install the pip packages on `requirements_embeddings.txt`. It is BGE and Qdrant-related packages. You can create a new python package or if you are running `speach_to_text` locally, you can just install the requirements on the same environment.

1. Run `pipeline_embeddins.py` (in the speach_to_text application/dir). You must download the `asr` folder for the speaker information and the `transcripts` folder for the episode transcripts. Download these folders from the 'output transcripts' directory on the shared TWIML-RAG Google Drive (request access via the TWIML slack community twiml-rag channel. (Note that this will be very slow on CPU only machine. GPU took about 5 minutes but CPU only took over 3 hours).

This will create
1. `info` folder with information about the episodes
2. `embeddings` folder with the dialogs cut up with 250 word size patches
3. Create embeddings using BGE and save to qdrant
   1.   Summary information from the info
   2. Patches of dialogs from the transcripts

### Azure Functions

Azure function code and website to run it.

1. `Node.js` is required to run the azure functions. Since azure functions don't run well on every version of node, we need to install the node version manager `nvm`. The instructions are as follows:
   ```bash
   wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
   
   source ~/.bashrc
   
   nvm install node
   ```
   and this should install the latest version of node.

1. To run the azure functions locally, install azurite and run it on a new directory to store the data
   ```
   npm install -g azurite
   azurite --silent --location .
   ``` 
   There is also a docker version available for azurite.
1. Install the dependencies in `requirements.txt`. The package `azure-functions` gives you the azure function capability.
1. Install the node `azure functions` using the command
   ```bash
   sudo npm install -g azure-functions-core-tools@3 --unsafe-perm true
   ```
1. Create the `config.py` file. It should have the following contents but the `OPENAI_API_KEY` must be populated since that is not done locally. The others can be left blank since we are using local versions of qdrant and embaas.
   ```python
   OPENAI_API_KEY = '<your openai api key>'
   QDRANT_URL = ""
   QDRANT_API_KEY = ""
   EMBAAS_API_KEY = ''
   ```
1. You can start your function using `func start`. The output should like the following:
   ```
   Azure Functions Core Tools
   Core Tools Version:       4.0.5455 Commit hash: N/A  (64-bit)
   Function Runtime Version: 4.27.5.21554
   
   [2023-12-28T04:12:55.343Z] Worker process started and initialized.
   
   Functions:

        embedfn:  http://localhost:7071/api/embedfn

        ragfn:  http://localhost:7071/api/ragfn

        ragfncheck:  http://localhost:7071/api/ragfncheck

        ragfnhist:  http://localhost:7071/api/ragfnhist

   For detailed output, run func with --verbose flag.
   ```

## Local Running (Browser)

1. We have to launch the web-browser without the CORS feature. For chrome, use `google-chrome --disable-web-security`.
2. Just load one of the html files in the `web_rag` folder and it should use local resources (can be switched to remote. Add the relevant API codes in the config.py). It still use the OpenAI API. 

