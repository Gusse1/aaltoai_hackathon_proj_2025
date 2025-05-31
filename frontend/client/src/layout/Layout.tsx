import { CContainer } from "@coreui/react";
import React from "react";
import Header from "./Header.tsx";
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
