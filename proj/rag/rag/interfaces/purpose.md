# wrappers via. inherited ABC classes or protocols to 
# help abstract from common api-functionality, so the
# calls are the same everywhere for the dev and all the
# pernickety details are handled behind the scenes for
# the particular api implementation (eg. diff for hugging
# face, diff for openai, diff for langchain.openai etc. 
# etc.)