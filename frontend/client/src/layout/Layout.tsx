import { CContainer } from "@coreui/react";
import React from "react";
import Header from "./Header.tsx";
import MainForm from "../forms/MainFrom.tsx";

const Layout = () => {
  return (
    <CContainer fluid className="main-content">
      <Header />
      <MainForm />
    </CContainer>
  );
};

export default Layout;
