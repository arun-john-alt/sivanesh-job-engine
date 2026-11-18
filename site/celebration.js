const banner = document.querySelector('.placement-banner');
const canvas = document.querySelector('#placement-confetti');
const motion = matchMedia('(prefers-reduced-motion: reduce)');
const context = canvas.getContext('2d');
const colors = ['#ad2d41', '#2852a8', '#fff8e5', '#e98295', '#632731'];
const animations = [];
let frame = 0;
let lastFrame = 0;
let elapsed = 0;
let particles = [];
let bounds;
let copyBounds;
let inView = true;

function loop(element, keyframes, duration, delay = 0) {
  const animation = element.animate(keyframes, {
    duration, delay, iterations: Infinity, direction: 'alternate', easing: 'ease-in-out'
  });
  animation.pause();
  animations.push(animation);
}

banner.querySelectorAll('.balloon').forEach((balloon, index) => {
  loop(balloon, [
    {transform: 'translateY(5px) rotate(-3deg)'},
    {transform: 'translateY(-9px) rotate(3deg)'}
  ], 2400 + index * 330, -index * 600);
});
banner.querySelectorAll('.party-flags g').forEach((flags, index) => {
  loop(flags, [{transform: 'rotate(-2.5deg)'}, {transform: 'rotate(2.5deg)'}], 1900 + index * 180, -index * 400);
});
banner.querySelectorAll('.party-sprinkles g').forEach((paper, index) => {
  loop(paper, [{transform: 'translateY(-3px) rotate(-1deg)'}, {transform: 'translateY(5px) rotate(1deg)'}], 2700 + index * 220, -index * 500);
});

function sizeConfetti() {
  bounds = banner.getBoundingClientRect();
  const copy = banner.querySelector('.placement-copy').getBoundingClientRect();
  copyBounds = {left: copy.left - bounds.left - 18, right: copy.right - bounds.left + 18,
    top: copy.top - bounds.top - 12, bottom: copy.bottom - bounds.top + 12};
  const ratio = Math.min(devicePixelRatio || 1, 2);
  canvas.width = Math.round(bounds.width * ratio);
  canvas.height = Math.round(bounds.height * ratio);
  context?.setTransform(ratio, 0, 0, ratio, 0, 0);
  particles = Array.from({length: bounds.width < 600 ? 55 : 105}, () => ({
    x: Math.random() * bounds.width,
    y: Math.random() * (bounds.height + 50) - 50,
    speed: 32 + Math.random() * 44,
    drift: (Math.random() - .5) * 20,
    size: 3 + Math.random() * 4,
    phase: Math.random() * Math.PI * 2,
    spin: (Math.random() - .5) * 3,
    color: colors[Math.floor(Math.random() * colors.length)],
    shape: Math.random() < .25 ? 'circle' : 'paper'
  }));
}

function drawConfetti(now) {
  const delta = lastFrame ? Math.min((now - lastFrame) / 1000, .05) : 0;
  lastFrame = now;
  elapsed += delta;
  context.clearRect(0, 0, bounds.width, bounds.height);
  for (const particle of particles) {
    particle.y += particle.speed * delta;
    particle.x += particle.drift * delta;
    if (particle.y > bounds.height + 20) { particle.y = -20; particle.x = Math.random() * bounds.width; }
    if (particle.x < -20) particle.x = bounds.width + 20;
    if (particle.x > bounds.width + 20) particle.x = -20;
    const x = particle.x + Math.sin(elapsed * 1.7 + particle.phase) * 10;
    // Keep the announcement clear while paper falls around it.
    if (x > copyBounds.left && x < copyBounds.right && particle.y > copyBounds.top && particle.y < copyBounds.bottom) continue;
    context.save();
    context.translate(x, particle.y);
    context.rotate(particle.phase + elapsed * particle.spin);
    context.scale(1, .35 + Math.abs(Math.cos(elapsed * 2 + particle.phase)) * .65);
    context.fillStyle = particle.color;
    if (particle.shape === 'circle') {
      context.beginPath();context.arc(0, 0, particle.size * .6, 0, Math.PI * 2);context.fill();
    } else context.fillRect(-particle.size / 2, -particle.size, particle.size, particle.size * 1.8);
    context.restore();
  }
  frame = requestAnimationFrame(drawConfetti);
}

function syncMotion() {
  const active = !motion.matches && !document.hidden && inView;
  animations.forEach(animation => active ? animation.play() : animation.pause());
  if (!active) {
    cancelAnimationFrame(frame);
    frame = 0;
    lastFrame = 0;
    context?.clearRect(0, 0, canvas.width, canvas.height);
  } else if (context && !frame) frame = requestAnimationFrame(drawConfetti);
}

new ResizeObserver(() => { sizeConfetti(); syncMotion(); }).observe(banner);
new IntersectionObserver(([entry]) => { inView = entry.isIntersecting; syncMotion(); }).observe(banner);
motion.addEventListener('change', syncMotion);
document.addEventListener('visibilitychange', syncMotion);
window.addEventListener('pagehide', () => {
  inView = false;
  syncMotion();
});
window.addEventListener('pageshow', () => { inView = true; syncMotion(); });
sizeConfetti();
syncMotion();
