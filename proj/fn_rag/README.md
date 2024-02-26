# Setting up the RAG Backend

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
