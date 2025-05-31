# Database Angler - AaltoAI 2025 hackathon project

This project is an AI-agent, which can answer questions from provided data. The agent can also produce visualizations when required and show the SQL code which was used to obtain the results. The agent should work with any kind of SQL database, but for testing we have used the Chinook Database (https://github.com/lerocha/chinook-database).

We are using React and TypeScript for the frontend, Python and Flask for the backend, and LangChain and Huggingface for the LLM prompts. The LLM used for testing was DeepSeek-R1-Distill-Qwen-32B, but the agent works also with other LLM's at least with very minor modifications. We have a web-based user interface, which runs locally. Flask handles the linking between the backend and our UI. LangChain pipelines some of the inference steps by guiding the LLM to first extract the number of output elements and then using that information in the SQL queries.

## Setup
To setup the software, please first install the packages from the requirements.txt using pip {pip install -r requirements.txt}.
You then need to configure your PostgreSQL database. Input your PostgreSQL username and password in the setup.env file in root. We have an example of such an env in the file setup.env.example.
You will also have to setup your huggingface_cli with your own API-token. You may adjust the model used using the same setup.env file to any that supports the huggingface transformers interface.
This code assumes that you are running the agent locally on your machine. Running the agent remotely using e.g. an API-token might need changes to the code.
Note: To use the agent with relatively large LLM's, you will need a lot of GPU VRAM.

To start up the software, run "python server.py" to open up the Flask server at localhost:5000 on your root. Then go to frontend/client folder, run "npm install" and then "npm start".

## Related problems
We have implemented error catching logic and the agent tries to call the LLM again if it fails to e.g. produce suitable SQL code. However, the agent might still produce faulty results, especially for more difficult questions. When the agent calls the LLM to give the desired number of elements, it sometimes produces unnecessary repetitive output, so we decided to extract only the relevant beginning of the output. We were not able to use smaller number of max_new_tokens (maximum number of output tokens) for the first LLM call, because the second LLM call, which produces the SQL code, required relatively many tokens. We were not able to create separate pipes for both LLM calls because in that case we ran out of GPU VRAM, so we had to adapt.
