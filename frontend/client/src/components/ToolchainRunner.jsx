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
        style={{ 
          maxHeight: '400px',
          width: '50%',
          maxWidth: '50%',
          overflow: 'auto',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          overflowWrap: 'anywhere',
          padding: '16px',
          fontFamily: 'monospace',
          backgroundColor: '#f8f9fa'
        }}
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
        <CCard className="output-card" style={{ 
          maxHeight: '400px',
          width: '50%',
          maxWidth: '50%',
          overflow: 'auto',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          overflowWrap: 'anywhere',
          padding: '16px',
          fontFamily: 'monospace',
          backgroundColor: '#f8f9fa'
        }}>
          <pre style={{ 
            margin: 0,
            padding: 0,
            width: '100%',
            maxWidth: '100%',
            boxSizing: 'border-box'
          }}>{output}</pre>
        </CCard>
      )}
    </CForm>
  );
}

export default ToolchainRunner;
