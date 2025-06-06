import React, { useState } from 'react';
import axios from 'axios';
import InputField from "../components/InputField.tsx";
import { CButton, CCard, CCardTitle, CForm, CCollapse, CSpinner } from "@coreui/react";
import { cilTerminal, cilCode, cilChevronBottom, cilChevronTop } from "@coreui/icons";
import { CIcon } from "@coreui/icons-react";
import figurePng from "../figure.png";

function ToolchainRunner() {
  const [input, setInput] = useState('');
  const [queryResults, setQueryResults] = useState('');
  const [sql, setSql] = useState('');
  const [showSql, setShowSql] = useState(false);
  const [showResults, setShowResults] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState('');
  const [hasVisualization, setHasVisualization] = useState(false);
  const [textResponse, setTextResponse] = useState('');
  const [imageModule, setImageModule] = useState(null);

  const runToolchain = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post(
        'http://localhost:5000/run-toolchain',
        { input }
      );

      setHasVisualization(response.data.visualization || false);
      setTextResponse(response.data.text_response || '');

      if (response.data.visualization) {
        const freshImage = await import('../figure.png');
        setImageModule(freshImage.default);
        } else {
        setImageModule(null);
      }

      setQueryResults(response.data.results || response.data.error || textResponse);
      setSql(response.data.sql || 'No SQL generated');
      setShowResults(true);
      setShowSql(false);
    } catch (error) {
      setQueryResults(`Error: ${error.message}`);
      setSql('');
      setHasVisualization(false);
      setImageUrl('');
    } finally {
      setIsLoading(false);
    }
  };

  const formatOutput = (output) => {
    if (!output) return '';
    if (output.startsWith('[') && output.endsWith(']')) {
      try {
        const data = JSON.parse(output.replace(/'/g, '"'));
        return data.map(row => JSON.stringify(row)).join('\n');
      } catch {
        return output;
      }
    }
    return output;
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  return (
    <CForm className="chat">
      <CCardTitle className="title">Welcome! How may I aid you?</CCardTitle>

      <InputField 
        style={{ 
          maxHeight: '1200px',
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
        placeholder="Enter input for DB query"
      />

      <CButton 
        className="button" 
        onClick={runToolchain} 
        disabled={isLoading || input.trim() === ''}
      >
        {isLoading ? 'Pondering...' : 'Submit'}
      </CButton>
      {isLoading && (
        <CSpinner className="spinner"></CSpinner>
      )}

      {(queryResults || sql || hasVisualization) && (
        <div style={{ 
          marginTop: '1rem',
          width: '50%',
          maxWidth: '50%'
        }}>
          {/* Query Results Section */}
          <div 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              cursor: 'pointer',
              marginBottom: '0.5rem'
            }}
            onClick={() => setShowResults(!showResults)}
          >
            <CIcon 
              icon={cilTerminal} 
              size="lg" 
              className="text-success" 
              style={{ marginRight: '0.5rem' }}
            />
            <span style={{ fontWeight: 'bold' }}>Query Results</span>
            <CIcon 
              icon={showResults ? cilChevronTop : cilChevronBottom} 
              style={{ marginLeft: 'auto' }}
            />
          </div>

          <CCollapse visible={showResults}>
            <CCard className="output-card" style={{ 
              padding: '1rem', 
              marginBottom: '1rem',
              width: '100%',
              overflowX: 'auto'
            }}>
              <pre style={{ 
                whiteSpace: 'pre-wrap',
                margin: 0,
                fontFamily: 'monospace',
                wordBreak: 'break-word'
              }}>{formatOutput(queryResults)}</pre>
            </CCard>
          </CCollapse>

          {/* SQL Section */}
          <div 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              cursor: 'pointer',
              marginBottom: '0.5rem'
            }}
            onClick={() => setShowSql(!showSql)}
          >
            <CIcon 
              icon={cilCode} 
              size="lg" 
              className="text-primary" 
              style={{ marginRight: '0.5rem' }}
            />
            <span style={{ fontWeight: 'bold' }}>Generated SQL</span>
            <CIcon 
              icon={showSql ? cilChevronTop : cilChevronBottom} 
              style={{ marginLeft: 'auto' }}
            />
          </div>

          <CCollapse visible={showSql}>
            <CCard className="output-card" style={{ 
              padding: '1rem',
              width: '100%',
              overflowX: 'auto'
            }}>
              <pre style={{ 
                whiteSpace: 'pre-wrap',
                margin: 0,
                fontFamily: 'monospace',
                color: '#6c757d',
                wordBreak: 'break-word'
              }}>{sql}</pre>
            </CCard>
          </CCollapse>

          {/* Visualization Section - Only shown when hasVisualization is true */}
          {hasVisualization && imageModule && (
            <div style={{ marginTop: '1rem', width: '100%', maxWidth: '100%' }}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontWeight: 'bold' }}>Generated Image</span>
              </div>
              <CCard style={{ padding: '1rem' }}>
                <img 
                  src={imageModule} 
                  alt="Generated visualization" 
                  style={{ maxWidth: '100%' }}
                  key={Date.now()} // Force new instance each time
                />
              </CCard>
            </div>
          )}
      </div>
      )}
    </CForm>
  );
}

export default ToolchainRunner;
