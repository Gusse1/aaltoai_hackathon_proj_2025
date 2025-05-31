import React from "react";
import { CFormTextarea } from "@coreui/react";

interface InputFieldProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  placeholder?: string;
}

const InputField: React.FC<InputFieldProps> = ({ 
  value, 
  onChange, 
  placeholder 
}) => {
  return (
    <CFormTextarea
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className="input-field"
      style={{ 
        resize: 'vertical'   // Allows user to resize vertically
      }}
      rows={8}  // Default visible rows
    />
  );
};

export default InputField;
