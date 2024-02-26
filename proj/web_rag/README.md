### RAG Frontend (Browser)

1. We have to launch the web-browser without the CORS feature. For chrome, use `google-chrome --disable-web-security`.
2. Just load one of the html files in the `web_rag` folder and it should use local resources (can be switched to remote. Add the relevant API codes in the config.py). It still use the OpenAI API. 