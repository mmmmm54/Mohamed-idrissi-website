/* Gentle wheel interpolation. Touch, pinch zoom, keyboard and nested scrollers
   keep their native behaviour. No third-party dependency or perpetual RAF. */
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const finePointer = matchMedia('(hover: hover) and (pointer: fine)');
let frame = 0;
let destination = window.scrollY;
let previousTime = 0;
const cancel = () => { cancelAnimationFrame(frame); frame = 0; previousTime = 0; destination = window.scrollY; };
const tick = (time: number) => {
  const elapsed = previousTime ? Math.min(time - previousTime, 48) : 16;
  previousTime = time;
  destination = Math.max(0, Math.min(destination, document.documentElement.scrollHeight - innerHeight));
  const distance = destination - window.scrollY;
  window.scrollTo({ top: Math.abs(distance) < 1 ? destination : window.scrollY + distance * (1 - Math.exp(-elapsed / 220)), behavior: 'instant' });
  if (Math.abs(distance) < 1) { frame = 0; previousTime = 0; }
  else frame = requestAnimationFrame(tick);
};
window.addEventListener('wheel', (event) => {
  if (reduced.matches || !finePointer.matches || event.ctrlKey || event.metaKey || event.shiftKey || Math.abs(event.deltaX) > Math.abs(event.deltaY)) { cancel(); return; }
  // Small, high-resolution deltas are usually already-smooth trackpad input.
  if (event.deltaMode === 0 && Math.abs(event.deltaY) < 40) { cancel(); return; }
  for (const element of event.composedPath()) {
    if (!(element instanceof HTMLElement) || element === document.body || element === document.documentElement) continue;
    if (element.matches('input, textarea, select, [contenteditable="true"]') || (/auto|scroll/.test(getComputedStyle(element).overflowY) && element.scrollHeight > element.clientHeight)) { cancel(); return; }
  }
  if (!event.cancelable) return;
  event.preventDefault();
  if (!frame) destination = window.scrollY;
  const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? innerHeight : 1;
  const delta = event.deltaY * unit * 0.55;
  if ((destination - window.scrollY) * delta < 0) destination = window.scrollY;
  // Keep rapid wheel bursts from building a long, difficult-to-stop queue.
  destination = window.scrollY + Math.max(-innerHeight * 0.65, Math.min(innerHeight * 0.65, destination + delta - window.scrollY));
  if (!frame) frame = requestAnimationFrame(tick);
}, { passive: false });
window.addEventListener('keydown', cancel);
window.addEventListener('pointerdown', cancel, { passive: true });
window.addEventListener('touchstart', cancel, { passive: true });
window.addEventListener('hashchange', cancel);
window.addEventListener('blur', cancel);
window.addEventListener('resize', cancel);
reduced.addEventListener('change', cancel);
