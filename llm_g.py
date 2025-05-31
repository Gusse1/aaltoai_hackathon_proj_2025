import sys
import os
from transformers import pipeline

def load_description():
    try:
        with open("database_description.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: database_description.txt not found in current directory")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: llm_g.py \"Your prompt here\"")
        sys.exit(1)

    database_description = load_description()  # Load from file
    prompt = sys.argv[1]

    pipe = pipeline(
        "text-generation",
        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        device_map="auto"
    )

    messages = [
        {"role": "system", "content": database_description},
        {"role": "user", "content": prompt}
    ]

    output = pipe(
        messages,
        max_new_tokens=2400,
        pad_token_id=pipe.tokenizer.eos_token_id
    )

    print("\nGenerated Output:")
    print(output[0]['generated_text'][-1]['content'])

if __name__ == "__main__":
    main()
