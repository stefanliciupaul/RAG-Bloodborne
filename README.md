WIP RAG System used to query for information related to the videogame Bloodborne.

Data was pulled from the website https://www.bloodborne-wiki.com/

Currently, the scraper is configured only to pull information from the boss pages.

The project is meant to be run locally on Intel Arc hardware and uses the OpenARC framework since Intel pulled support from its IPEX-LLM library https://github.com/intel/ipex-llm

Qwen3 models in the OpenVINO format are used for embedding the chunks, generation and reranking the chunks from which the model sources the answer. 

Currently the three models in use are: 
For generation - https://huggingface.co/OpenVINO/Qwen3-14B-int4-ov
For embedding - https://huggingface.co/OpenVINO/Qwen3-Embedding-0.6B-int4-cw-ov
For reranking - https://huggingface.co/OpenVINO/Qwen3-Reranker-0.6B-int8-ov

Commands needed to run:
- Scraping the pages from the wiki and creating the chunks
python parsing/main.py
- Setting up the vector store
python generation/embed_store.py
- Running the app in the CLI
python generation/cli.py

