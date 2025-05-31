import { CContainer } from "@coreui/react";
import React from "react";
import Header from "./Header.tsx";
import MainForm from "../forms/MainFrom.tsx";
import ToolchainRunner from "../components/ToolchainRunner.jsx";

const Layout = () => {
  return (
    <CContainer fluid className="main-content">
      <Header />
      <ToolchainRunner />
    </CContainer>
  );
};

export default Layout;
