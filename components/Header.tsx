import React from "react";

const Header: React.FC = () => {
  return (
    <header
      style={{
        backgroundColor: "#F0F4FF",
        color: "#1A237E",
        padding: "16px 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <span style={{ fontSize: "24px" }}>🧾</span>
        <h1
          style={{
            margin: 0,
            fontSize: "20px",
            fontWeight: "700",
            color: "#1A237E",
            letterSpacing: "-0.3px",
          }}
        >
          영수증 지출관리
        </h1>
      </div>
      <nav style={{ display: "flex", gap: "20px" }}>
        <a
          href="/"
          style={{
            color: "#3949AB",
            textDecoration: "none",
            fontWeight: "600",
            fontSize: "14px",
          }}
        >
          홈
        </a>
        <a
          href="/history"
          style={{
            color: "#3949AB",
            textDecoration: "none",
            fontWeight: "600",
            fontSize: "14px",
          }}
        >
          지출 내역
        </a>
        <a
          href="/upload"
          style={{
            color: "#3949AB",
            textDecoration: "none",
            fontWeight: "600",
            fontSize: "14px",
          }}
        >
          영수증 업로드
        </a>
      </nav>
    </header>
  );
};

export default Header;
