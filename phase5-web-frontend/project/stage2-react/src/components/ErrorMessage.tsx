// =====================================================
// components/ErrorMessage.tsx
// =====================================================

interface ErrorMessageProps {
  message: string;
}

export function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <div
      role="alert"
      style={{
        color: "#cc0000",
        border: "1px solid #cc0000",
        borderRadius: 8,
        padding: "12px 16px",
        background: "#fff0f0",
        marginBottom: 16,
      }}
    >
      {message}
    </div>
  );
}
