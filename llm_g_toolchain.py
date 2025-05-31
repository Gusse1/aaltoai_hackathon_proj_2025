import sys
import re
from transformers import pipeline
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFacePipeline
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from sqlalchemy import create_engine, inspect
from sqlalchemy import MetaData  # Add this import at the top

DB_URI = "postgresql://llm_user:secure_password123@localhost:5432/chinook"

def get_available_tables():
    engine = create_engine(DB_URI)
    inspector = inspect(engine)
    return inspector.get_table_names()

def main():
    # 1. Initialize LLM
    pipe = pipeline(
        "text-generation",
        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        device_map="auto",
        max_new_tokens=500,
        temperature=0.1
    )
    llm = HuggingFacePipeline(pipeline=pipe)

    # 2. Connect to database
    available_tables = get_available_tables()
    print(f"Available tables: {available_tables}")
    db = SQLDatabase.from_uri(
        DB_URI,
        include_tables=None,  # None includes all tables
        sample_rows_in_table_info=3,  # Optimal sample size
        metadata=MetaData(schema="public")  # Note: MetaData (not Metadata)
    )
    print(db.get_table_info())  # Verify schema visibility
    # 3. Create strict prompt template
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
    # 4. Create chain
    chain = create_sql_query_chain(llm, db, prompt=prompt)

    # 5. Get question
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "List 5 artists"

    try:
        # 6. Get and clean the result
        result = chain.invoke({
            "question": question,
            "top_k": 5
        })

        # Clean the output
        result = re.sub(r'&quot;', '"', result)  # Replace HTML entities
        result = re.search(r'(SELECT.*?)(?:;|$)', result, re.DOTALL | re.IGNORECASE).group(1) + ";"

        print("\n=== Generated SQL ===")
        print(result)

        print("\n=== Query Results ===")
        print(db.run(result))

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
