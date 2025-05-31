import React, { useState } from 'react';
import axios from 'axios';

function ToolchainRunner() {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const runToolchain = async () => {
    setIsLoading(true);
    try {
      // For GET version:
      // const response = await axios.get(
      //   'http://localhost:5000/run-toolchain',
      //   { params: { input } }
      // );

      // For POST version:
      const response = await axios.post(
        'http://localhost:5000/run-toolchain',
        { input }
      );

      setOutput(response.data.output || response.data.error);
    } catch (error) {
      setOutput(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Enter input for LLM toolchain"
      />
      <button onClick={runToolchain} disabled={isLoading}>
        {isLoading ? 'Running...' : 'Run Toolchain'}
      </button>
      <pre>{output}</pre>
    </div>
  );
}

export default ToolchainRunner;
