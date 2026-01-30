export class Scroller {
  constructor(
    element,
    {
      smooth = false,
      toleranceRem = 2,
      reapplyDelayMs = 0,
      reapplyToleranceRatio = 0,
    } = {},
  ) {
    this.element = element;
    this.smooth = smooth;
    this.reapplyDelayMs = reapplyDelayMs;
    this.reapplyToleranceRatio = reapplyToleranceRatio;
    this.tolerance =
      toleranceRem *
      parseFloat(getComputedStyle(document.documentElement).fontSize);
    this.wasAtBottom = this.isAtBottom();
    this._scrollListener = null;
  }

  _getEffectiveScrollTop() {
    const scrollingToRaw = this.element?.dataset?.scrollingTo;
    const scrollingTo = scrollingToRaw == null ? null : Number(scrollingToRaw);
    if (Number.isFinite(scrollingTo)) return scrollingTo;
    return this.element.scrollTop;
  }

  _setScrollingTo(target) {
    this.element.dataset.scrollingTo = String(target);

    if (this._scrollListener) return;

    this._scrollListener = () => {
      const current = this.element.scrollTop;
      const activeTargetRaw = this.element?.dataset?.scrollingTo;
      const activeTarget = activeTargetRaw == null ? null : Number(activeTargetRaw);
      if (!Number.isFinite(activeTarget)) {
        this._clearScrollingTo();
        return;
      }

      if (current >= activeTarget - 1) this._clearScrollingTo();
    };

    this.element.addEventListener("scroll", this._scrollListener, {
      passive: true,
    });
  }

  _clearScrollingTo() {
    delete this.element.dataset.scrollingTo;
    if (this._scrollListener) {
      this.element.removeEventListener("scroll", this._scrollListener);
      this._scrollListener = null;
    }
  }

  isAtBottom() {
    const { scrollHeight, clientHeight } = this.element;
    const scrollTop = this._getEffectiveScrollTop();
    return scrollHeight - scrollTop - clientHeight <= this.tolerance;
  }

  _getBottomDistancePx() {
    const { scrollHeight, clientHeight } = this.element;
    const scrollTop = this._getEffectiveScrollTop();
    return scrollHeight - scrollTop - clientHeight;
  }

  scrollToBottom() {
    const target = Math.max(
      0,
      this.element.scrollHeight - this.element.clientHeight,
    );
    if (this.smooth) {
      this._setScrollingTo(target);
      this.element.scrollTo({ top: target, behavior: "smooth" });
    } else {
      this._clearScrollingTo();
      this.element.scrollTop = target;
    }
  }

  _getReapplyTimeoutId() {
    const raw = this.element?.dataset?.scrollerTimeout;
    const parsed = raw == null ? null : Number(raw);
    if (!Number.isFinite(parsed)) return null;
    return parsed;
  }

  _clearReapplyTimeout() {
    const id = this._getReapplyTimeoutId();
    if (id != null) clearTimeout(id);
    delete this.element.dataset.scrollerTimeout;
  }

  _scheduleReapplyScrollToBottom() {
    this._clearReapplyTimeout();

    const id = setTimeout(() => {
      delete this.element.dataset.scrollerTimeout;

      if (!this.wasAtBottom) return;
      if (!this.isAtBottom()) return;

      this.scrollToBottom();
    }, this.reapplyDelayMs);

    this.element.dataset.scrollerTimeout = String(id);
  }

  reApplyScroll(instant = false) {
    this._clearReapplyTimeout();

    if (!this.wasAtBottom) return;

    if (instant) {
      this.scrollToBottom();
      return;
    }

    if (!this.isAtBottom()) {
      this.scrollToBottom();
      return;
    }

    const ratio = this.reapplyToleranceRatio;
    if (ratio <= 0) {
      if (this.reapplyDelayMs > 0) this._scheduleReapplyScrollToBottom();
      else this.scrollToBottom();
      return;
    }

    const dist = this._getBottomDistancePx();
    const tolerance = this.tolerance;
    const clampedDist = Math.max(0, Math.min(dist, tolerance));
    const progress = tolerance > 0 ? 1 - clampedDist / tolerance : 1;
    if (progress < ratio) return;

    if (this.reapplyDelayMs > 0) this._scheduleReapplyScrollToBottom();
    else this.scrollToBottom();
  }
}
