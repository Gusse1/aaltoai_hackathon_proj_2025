from flask import Flask, request, jsonify
import subprocess
import shlex  # For safe command splitting

app = Flask(__name__)

# GET version (simple but less secure)
@app.route('/run-toolchain', methods=['GET'])
def run_toolchain_get():
    try:
        # Get user input from query parameters
        user_input = request.args.get('input', '')

        # Run the command (adjust paths as needed)
        result = subprocess.run(
            ["python3", "llm_g_toolchain.py", user_input],
            capture_output=True,
            text=True
        )

        return jsonify({
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST version (more secure)
@app.route('/run-toolchain', methods=['POST'])
def run_toolchain_post():
    try:
        data = request.get_json()
        user_input = data.get('input', '')

        # Sanitize input if needed
        # user_input = shlex.quote(user_input)  # Basic protection

        result = subprocess.run(
            ["python3", "llm_g_toolchain.py", user_input],
            capture_output=True,
            text=True
        )

        return jsonify({
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
