import sys
import re
from transformers import pipeline
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_huggingface import HuggingFacePipeline
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from sqlalchemy import create_engine, inspect
from langchain_core.output_parsers import StrOutputParser
import gc
import torch

DB_URI = "postgresql://llm_user:secure_password123@localhost:5432/chinook"

def get_available_tables():
    engine = create_engine(DB_URI)
    inspector = inspect(engine)
    return inspector.get_table_names()

def main():
    def extract_number(text: str) -> int:
        print(f"\n=== DEBUG RAW LLM OUTPUT ===\n{text}\n{'='*30}")

        # Extract first number after the marker text
        marker = "THE FINAL OUTPUT NUMBER BASED ON THIS USER INPUT IS:"
        marker_pos = text.find(marker)

        if marker_pos != 0:  # If marker is found
            remaining_text = text[marker_pos + len(marker):]  # Get text after marker
            numbers = [int(match) for match in re.findall(r'\b\d+\b', remaining_text)]
            if numbers:
                print(numbers)
                return numbers[0]  # Take first number after marker and clamp

        return 0  # Return 0 if marker not found or no numbers after it
    limit_prompt = ChatPromptTemplate.from_template("""
    You are a strict preprocessing agent. Your ONLY job is to determine how many results the user wants.

    #RULES:
    If the user clearly asks for a number of results (e.g., "top 5", "show 20", "I want 3"), return that number.
    If there is not a number very clearly mentioned, immediately give 0 as output.
    Do NOT guess or infer. Only extract the number from user input or return 0.

    FORMAT:
    Return ONLY the number. No text, no explanation, no punctuation.

    EXAMPLES:
    User: Give me 3 best tracks
    Output: 3

    User: List top 10 albums
    Output: 10

    User: Who are the best artists?
    Output: 0

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
        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        #model="meta-llama/Llama-3.1-8B",
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
    max_retries = 3
    top_k = None

    #for attempt in range(max_retries):
    try:
        top_k = int(limit_chain.invoke({"input": question}))
        print("TOP K IS THIS NUMBER!!!!!  ", top_k)
        if top_k == 0:
            #if attempt < max_retries-1:
            #    print("Retrying.")
            #else:
            print("LLM failed to identify top_k. Closing")
            sys.exit(1)
        else:
            #break
            pass
    except Exception as e:
        print(f"Error: {e}")
        #if attempt < max_retries:
        #    print("Retrying.")
        #else:
        print("LLM failed to identify top_k. Closing")
        sys.exit(1)

    available_tables = get_available_tables()
    print(f"Available tables: {available_tables}")
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

    for attempt in range(max_retries):
        try:
            result = chain.invoke({
                "question": question,
                "top_k": top_k
            })

            result = re.sub(r'&quot;', '"', result)  # Replace HTML entities
            result = re.search(r'(SELECT.*?)(?:;|$)', result, re.DOTALL | re.IGNORECASE).group(1) + ";" # Extract the first complete SQL SELECT query from the result

            print("\n=== Generated SQL ===")
            print(result)

            print("\n=== Query Results ===")
            print(db.run(result))
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            if attempt < max_retries:
                print("Retrying...")

if __name__ == "__main__":
    main()
