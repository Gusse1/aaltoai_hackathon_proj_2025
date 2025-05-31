import React, { useState } from 'react';
import axios from 'axios';
import InputField from "../components/InputField.tsx";
import { CButton, CCard, CCardTitle, CForm } from "@coreui/react";

function ToolchainRunner() {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const runToolchain = async () => {
    setIsLoading(true);
    try {
      console.log('Sending input:', input); // Debug log
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

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  return (
    <CForm className="chat">
      <CCardTitle className="title">Toolchain Runner</CCardTitle>

      <InputField 
        value={input}
        onChange={handleInputChange}
        placeholder="Enter input for LLM toolchain"
      />

      <CButton 
        className="button" 
        onClick={runToolchain} 
        disabled={isLoading}
      >
        {isLoading ? 'Running...' : 'Run Toolchain'}
      </CButton>

      {output && (
        <CCard className="output-card">
          <pre>{output}</pre>
        </CCard>
      )}
    </CForm>
  );
}

export default ToolchainRunner;
