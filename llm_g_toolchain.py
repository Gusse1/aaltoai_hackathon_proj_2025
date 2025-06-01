import sys
import re
import torch
from transformers import pipeline
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_huggingface import HuggingFacePipeline
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv
import ast
import pandas as pd
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Union
import json
import matplotlib.pyplot as plt

load_dotenv("setup.env")
db_uri = os.getenv("DATABASE_URI")
hf_model = os.getenv("HF_MODEL_NAME")

DB_URI = db_uri

def get_available_tables():
    engine = create_engine(DB_URI)
    inspector = inspect(engine)
    return inspector.get_table_names()

def main():
    def extract_number(text: str) -> int:
        #print(f"\n=== DEBUG RAW LLM OUTPUT ===\n{text}\n{'='*30}")

        # Extract first number after the marker text
        marker = "THE FINAL OUTPUT NUMBER BASED ON THIS USER INPUT IS:"
        marker_pos = text.find(marker)

        if marker_pos != -1:  # Marker found anywhere in the text
            remaining_text = text[marker_pos + len(marker):]  # Get text after marker
            number = re.search(r'\b\d+\b', remaining_text)
            if number:
                first_number = int(number.group(0))
                return first_number

        return 0  # Return 0 if marker not found or no numbers after it

    limit_prompt = ChatPromptTemplate.from_template("""
    You are a strict preprocessing agent. Your ONLY job is to determine how many results the user wants.

    #RULES:
    If the user clearly asks for a number of results (e.g., "top 5", "show 20", "I want 3"), return that number.
    If there is not a number very clearly mentioned, but the input makes sense for a database query, then
    infer a logical number (eg. 5). If the query makes no sense for a database query (eg. gibberish), then return 0.

    FORMAT:
    Return ONLY the number. No text, no explanation, no punctuation.

    EXAMPLES:
    User: Give me 3 best tracks
    Output: 3

    User: List top 10 albums
    Output: 10

    User: Who are the best artists?
    Output: 5

    User: something
    Output: 0

    User: I want 1000 rows
    Output: 100

    User: Which tracks are good?
    Output: 0

    ## EXAMPLES END HERE

    HERE IS THE REAL USER INPUT: {input}
    THE FINAL OUTPUT NUMBER BASED ON THIS USER INPUT IS: 
    """)

    pipe = pipeline(
        "text-generation",
        model=hf_model,
        device_map="auto",
        max_new_tokens=512,
        temperature=0.15
    )
    llm = HuggingFacePipeline(pipeline=pipe)

    limit_chain = limit_prompt | llm | StrOutputParser() | extract_number
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        print("Please provide a suitable question as command line argument.")
        sys.exit(1)
    top_k = None

    try:
        top_k = int(limit_chain.invoke({"input": question}))
        if top_k == 0:
            print("LLM failed to identify top_k. Closing")
            sys.exit(1)
        else:
            pass
    except Exception as e:
        print(f"Error: {e}")
        print("LLM failed to identify top_k. Closing")
        sys.exit(1)

    available_tables = get_available_tables()
    db = SQLDatabase.from_uri(
        DB_URI,
        include_tables=None,  # None includes all tables
        sample_rows_in_table_info=5
    )

    prompt = PromptTemplate.from_template("""
    You are a PostgreSQL expert. Generate EXACTLY ONE VALID SQL query for the Chinook database.
    Follow these rules STRICTLY:
    1. Use ONLY these tables: {table_info}
    2. NEVER use placeholder syntax like "..."
    3. Always include a proper WHERE clause if filtering
    4. Return ONLY the SQL, no explanations

    Question: {input}
    Number of results to return: {top_k} 
    SQLQuery:
    """)

    chain = create_sql_query_chain(llm, db, prompt=prompt)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = chain.invoke({
                "question": question,
                "top_k": top_k
            })

            result = re.sub(r'&quot;', '"', result)  # Replace HTML entities
            query = re.search(r'(SELECT.*?)(?:;|$)', result, re.DOTALL | re.IGNORECASE).group(1) + ";" # Extract the first complete SQL SELECT query from the result

            print("\n=== Generated SQL ===")
            print(query)
            
            print("\n=== Query Results ===")
            table = (db.run(query))
            #print(table)
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            if attempt < max_retries:
                print("Retrying...")
            else:
                sys.exit(1)

    def extract_plot_info(text: str) -> Union[dict, None]:

        # Extract json after marker
        marker = "Result:"
        marker_pos = text.find(marker)

        if marker_pos != -1:  # If marker is found

            try:
                remaining_text = text[marker_pos + len(marker):]  # Get text after marker
                #print(remaining_text)
                match = re.findall(r'\{.*?\}', remaining_text, re.DOTALL)
                #print(match)
                if not match:
                    print("No valid JSON object found.")
                    return None
                
                json_string = match[0]
                #print(f"JSON MATCH: {json_string}")
                json_object = json.loads(json_string)
                #print(json_object)
                return json_object
            except Exception as e:
                raise

        return None

    file_path = "database_description.txt"

    with open(file_path, "r", encoding="utf-8") as file:
        data_schema = file.read()

    plot_prompt = ChatPromptTemplate.from_template("""
    Given a user's question, a database schema, and the SQL query answering to the question, extract the following information:

    - Does the question require visualization (true) or is a text response more suitable (false), for example if resulting table is only one value                                                  
    - Suitable plot type for visualization: "bar/line" (if applicable)
    - Column names for the used columns in the resulting table (if applicable)
    - Suitable title for the plot (if applicable)
    - Text response depicting the answer to the question if no visualization is needed (if applicable)

    Question: {user_question}                                                                                                                                                               
    Query: {sql_query}
    Data schema: {data_schema}
    Query result: {query_output}
    
    Please output only the JSON object with no explanation, tags, or extra text. Follow below format:

    {{
    "visualization_boolean": true,
    "plot_type": "bar",
    "column_names": ["column1", "column2"],
    "title": "Descriptive plot title",
    "text_response": null
    }}

    OR

    {{
    "visualization_boolean": false,
    "plot_type": null,
    "column_names": null,
    "title": null,
    "text_response": "The average price of an album is 19.99 dollars."
    }}

    Result:                   
    """)

    plot_chain = plot_prompt | llm | StrOutputParser()

    for attempt in range(max_retries):
        try:
            raw_output = plot_chain.invoke({"user_question": question, "sql_query": query, "data_schema": data_schema, "query_output": table})

            plot_info = extract_plot_info(raw_output)
            print(plot_info)

            output_dir = "frontend/client/src/"
            filename = "figure.png"
            file_path = os.path.join(output_dir, filename)

            # Check if output requires visualization or not
            if not plot_info or not plot_info.get("visualization_boolean"):
                print("NO VISUALIZATION")
                #print("\n=== Query Results ===")
                text_response = plot_info.get("text_response") if plot_info else "No response available."
                print(text_response)
                break
            else:
                print("YES VISUALIZATION")
                plot_type = plot_info["plot_type"].lower()
                column_names = plot_info["column_names"]
                title = plot_info["title"]

                if not column_names or len(column_names) < 2:
                    raise ValueError("At least two column names (x and y) are required.")   

                if isinstance(table, str):
                    data = ast.literal_eval(table)
                else:
                    data = table
                df = pd.DataFrame(data, columns=plot_info["column_names"])
                df = df.round(2)
                #print("\n=== Query Results ===")
                print(df.to_string(index=False))

                x_col = column_names[0]
                y_col = column_names[1]

                #print(x_col)
                #print(y_col)
                plt.figure(figsize=(10, 6))

                if plot_type == "line":
                    plt.plot(df[x_col], df[y_col])
                elif plot_type == "bar":
                    x_labels = df[column_names[0]]
                    y_values = df[column_names[1]]

                    x = range(len(df))  # numeric positions for bars

                    plt.bar(x, y_values, width=0.5)
                    plt.xticks(ticks=x, labels=x_labels, rotation=45, ha='right')
                else:
                    break

                plt.title(title)
                plt.xlabel(x_col)
                plt.ylabel(y_col)
                plt.tight_layout()
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.savefig(file_path, dpi=300)
                plt.show()
                break
        except Exception as e:
            print(f"Error: {str(e)}")
            if attempt < max_retries:
                print("Retrying...")
            else:
                sys.exit(1)
if __name__ == "__main__":
    main()
