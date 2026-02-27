import { useEffect } from "react";
import "./Modal.css";

export interface ModalAction {
  label: string;
  onClick: () => void;
  variant?: "primary" | "secondary" | "danger";
}

interface ModalProps {
  isOpen: boolean;
  title: string;
  description?: string;
  actions?: ModalAction[];
  onClose: () => void;
  children?: React.ReactNode;
}

export default function Modal({
  isOpen,
  title,
  description,
  actions = [],
  onClose,
  children,
}: ModalProps) {
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-overlay" role="presentation" onClick={onClose}>
      <section
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="modal-panel"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal-header">
          <h2>{title}</h2>
          <button
            type="button"
            className="modal-close"
            aria-label="Close modal"
            onClick={onClose}
          >
            x
          </button>
        </header>
        {description && <p className="modal-description">{description}</p>}
        {children && <div className="modal-body">{children}</div>}
        {actions.length > 0 && (
          <footer className="modal-actions">
            {actions.map((action) => (
              <button
                key={action.label}
                type="button"
                className={`modal-action ${action.variant ?? "secondary"}`}
                onClick={action.onClick}
              >
                {action.label}
              </button>
            ))}
          </footer>
        )}
      </section>
    </div>
  );
}

