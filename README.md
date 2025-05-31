# Database Angler - aaltoai_hackathon_proj_2025

## Setup

This software should work with any kind of SQL database, but for testing we have used the Chinook DB (https://github.com/lerocha/chinook-database).

We are using React for the frontend, Python and Flask for the backend, and Langchain and Huggingface for the LLM prompts.

To setup the software, please first install the packages from the requirements.txt using pip {pip install -r requirements.txt}

Then configure your PSQL database. Input your psql user username and password in the setup.env file in root. We have an example of such an env file file setup.env.example.

You will also have to setup your huggingface_cli with your own API token. You may adjust the model used using the same setup.env file to any that supports the huggingface transformers interface.

This code assumes that you are running an LLM locally on your machine. Running an LLM remotely using eg. an api token might need changes to the code.