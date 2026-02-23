import { useCallback, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import "./SplitPane.css";

type Orientation = "vertical" | "horizontal";

interface SplitPaneProps {
  orientation: Orientation;
  primary: ReactNode;
  secondary: ReactNode;
  defaultPrimarySize?: number;
  minPrimarySize?: number;
  maxPrimarySize?: number;
  className?: string;
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

export default function SplitPane({
  orientation,
  primary,
  secondary,
  defaultPrimarySize = 45,
  minPrimarySize = 25,
  maxPrimarySize = 75,
  className,
}: SplitPaneProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [primarySize, setPrimarySize] = useState(
    clamp(defaultPrimarySize, minPrimarySize, maxPrimarySize),
  );

  const updateSizeFromPointer = useCallback(
    (clientX: number, clientY: number) => {
      const container = containerRef.current;
      if (!container) {
        return;
      }

      const rect = container.getBoundingClientRect();
      if (orientation === "vertical") {
        const next = ((clientX - rect.left) / rect.width) * 100;
        setPrimarySize(clamp(next, minPrimarySize, maxPrimarySize));
        return;
      }

      const next = ((clientY - rect.top) / rect.height) * 100;
      setPrimarySize(clamp(next, minPrimarySize, maxPrimarySize));
    },
    [maxPrimarySize, minPrimarySize, orientation],
  );

  const onPointerDown = (event: React.PointerEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);

    const onPointerMove = (moveEvent: PointerEvent) => {
      updateSizeFromPointer(moveEvent.clientX, moveEvent.clientY);
    };

    const onPointerUp = () => {
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
    };

    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);
  };

  useEffect(() => {
    setPrimarySize(clamp(defaultPrimarySize, minPrimarySize, maxPrimarySize));
  }, [defaultPrimarySize, maxPrimarySize, minPrimarySize]);

  const onKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    const step = 2;
    const decreaseKeys = orientation === "vertical" ? ["ArrowLeft"] : ["ArrowUp"];
    const increaseKeys = orientation === "vertical" ? ["ArrowRight"] : ["ArrowDown"];

    if (decreaseKeys.includes(event.key)) {
      event.preventDefault();
      setPrimarySize((prev) => clamp(prev - step, minPrimarySize, maxPrimarySize));
      return;
    }

    if (increaseKeys.includes(event.key)) {
      event.preventDefault();
      setPrimarySize((prev) => clamp(prev + step, minPrimarySize, maxPrimarySize));
      return;
    }

    if (event.key === "Home") {
      event.preventDefault();
      setPrimarySize(minPrimarySize);
      return;
    }

    if (event.key === "End") {
      event.preventDefault();
      setPrimarySize(maxPrimarySize);
    }
  };

  return (
    <div
      ref={containerRef}
      className={`split-pane split-pane--${orientation}${className ? ` ${className}` : ""}`}
      style={{ ["--primary-size" as string]: `${primarySize}%` }}
    >
      <div className="split-pane-primary">{primary}</div>

      <div
        className="split-pane-separator"
        role="separator"
        aria-orientation={orientation}
        aria-valuemin={minPrimarySize}
        aria-valuemax={maxPrimarySize}
        aria-valuenow={Math.round(primarySize)}
        aria-label={orientation === "vertical" ? "Resize panels horizontally" : "Resize panels vertically"}
        tabIndex={0}
        onPointerDown={onPointerDown}
        onKeyDown={onKeyDown}
      />

      <div className="split-pane-secondary">{secondary}</div>
    </div>
  );
}
