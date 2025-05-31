from flask import Flask, request, jsonify
import subprocess
import re

app = Flask(__name__)

@app.route('/run-toolchain', methods=['POST'])
def run_toolchain_post():
    try:
        data = request.get_json()
        user_input = str(data.get('input', ''))

        result = subprocess.run(
            ["python3", "llm_g_toolchain.py", user_input],
            capture_output=True,
            text=True
        )

        output = result.stdout

        # Check for visualization flag
        if "YES VISUALIZATION" in output:
            # Extract everything after YES VISUALIZATION
            vis_match = re.search(r'YES VISUALIZATION\n(.*)', output, re.DOTALL)
            visualization_data = vis_match.group(1).strip() if vis_match else None
            return jsonify({
                "success": result.returncode == 0,
                "visualization": True,
                "results": visualization_data,
                "error": result.stderr
            })
        else:
            # Original SQL and results parsing
            sql_match = re.search(r'=== Generated SQL ===\n(.*?)\n=== Query Results ===', output, re.DOTALL)
            results_match = re.search(r'=== Query Results ===\n(.*)', output, re.DOTALL)

            sql = sql_match.group(1).strip() if sql_match else None
            query_results = results_match.group(1).strip() if results_match else None

            return jsonify({
                "success": result.returncode == 0,
                "sql": sql,
                "results": query_results,
                "error": result.stderr
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
