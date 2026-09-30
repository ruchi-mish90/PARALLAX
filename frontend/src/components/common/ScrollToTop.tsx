import { useEffect } from "react";
import { useLocation } from "react-router-dom";

/**
 * Ensures that every route transition immediately resets scroll position to the top of the viewport.
 * This guarantees true multi-page document isolation rather than preserving prior scroll depths.
 */
export function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    // Reset window scroll immediately upon route change
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: "instant" as ScrollBehavior,
    });
  }, [pathname]);

  return null;
}

export default ScrollToTop;
