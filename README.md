# Database Angler - AaltoAI 2025 hackathon project

This project is an AI-agent, which can answer questions from provided data. The agent can also produce visualizations when required and show the SQL code which was used to obtain the results. The agent should work with any kind of SQL database, but for testing we have used the Chinook Database (https://github.com/lerocha/chinook-database).

We are using React for the frontend, Python and Flask for the backend, and LangChain and Huggingface for the LLM prompts.
We have a web-based user interface, which runs locally. Flask handles the linking between the backend and our UI. LangChain pipelines some of the inference steps by guiding the LLM to first extract the number of output elements and then using that information in the SQL queries.

To setup the software, please first install the packages from the requirements.txt using pip {pip install -r requirements.txt}.
You need to configure your PostgreSQL database. Input your PostgreSQL username and password in the setup.env file in root. We have an example of such an env in the file setup.env.example.
You will also have to setup your huggingface_cli with your own API-token. You may adjust the model used using the same setup.env file to any that supports the huggingface transformers interface.
This code assumes that you are running an LLM locally on your machine. Running an LLM remotely using e.g. an API-token might need changes to the code.

To start up the software, do python server.py to open up the flask server at localhost:5000 on your root. Then go into frontend/client folder, run npm install and then npm start.