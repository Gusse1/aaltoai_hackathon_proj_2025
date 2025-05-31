import sys
import re
from transformers import pipeline
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_huggingface import HuggingFacePipeline
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from sqlalchemy import create_engine, inspect
from sqlalchemy import MetaData  # Add this import at the top
from langchain_core.output_parsers import StrOutputParser

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

    def extract_number(text: str) -> int:
        print(f"\n=== DEBUG RAW LLM OUTPUT ===\n{text}\n{'='*30}")

        # First try: Extract last number in output (most likely the final answer)
        numbers = [int(match) for match in re.findall(r'\b\d+\b', text)]
        if numbers:
            return max(1, min(numbers[-1], 100))  # Take last number and clamp

        # Fallback: Parse XML-style tags if present
        if "</think>" in text:
            post_think = text.split("</think>")[-1]
            numbers = [int(match) for match in re.findall(r'\b\d+\b', post_think)]
            if numbers:
                return max(1, min(numbers[0], 100))

        print("Warning: No parsable number, defaulting to 5")
        return 5

    # Modified prompt for better compliance
    limit_prompt = ChatPromptTemplate.from_template("""
    Respond ONLY with an integer between 1-100 representing how many results to return.
    Use these guidelines:
    - 1 for existence checks
    - 5 for specific queries
    - 10-20 for listings
    - Never exceed 100

    Query: {input}
    Number:""")
    limit_chain = limit_prompt | llm | StrOutputParser() | extract_number
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])

    # Usage:
    top_k = limit_chain.invoke({"input": question})  # Already returns int
    print("TOP K \n\n\n", top_k)
    # 2. Connect to database
    available_tables = get_available_tables()
    print(f"Available tables: {available_tables}")
    db = SQLDatabase.from_uri(
        DB_URI,
        include_tables=None,  # None includes all tables
        sample_rows_in_table_info=5,  # Optimal sample size
        #metadata=MetaData(schema="public")  # Note: MetaData (not Metadata)
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

    try:
        # 6. Get and clean the result
        result = chain.invoke({
            "question": question,
            "top_k": top_k
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
