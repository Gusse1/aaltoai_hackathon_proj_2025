import React from "react";
import InputField from "../components/InputField.tsx";
import { CButton, CCard, CCardTitle, CForm } from "@coreui/react";

const MainForm = () => {
  return (
    <CForm className="chat">
      <CCardTitle className="title">Chat :DD</CCardTitle>
      <InputField />
      <CButton className="button">Submit</CButton>
    </CForm>
  );
};

export default MainForm;
