import { CHeader } from "@coreui/react";
import React from "react";
import logo from '../angler.svg';

const Header = () => {
  return (
    <CHeader className="header">
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '1rem',
        padding: '1rem'
      }}>
        <img src={logo} alt="Logo" style={{ width: '32px', height: '32px' }} />
        <div style={{
          fontSize: "1.5rem",
          fontWeight: "bold",
          color: "#ffffff"
        }}>
          Database Angler
        </div>
      </div>
    </CHeader>
  );
};

export default Header;
