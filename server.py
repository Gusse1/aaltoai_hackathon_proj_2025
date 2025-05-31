from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/run-toolchain', methods=['POST'])
def run_toolchain_post():
    try:
        data = request.get_json()
        user_input =str(data.get('input', ''))

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
