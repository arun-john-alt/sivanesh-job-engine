const banner = document.querySelector('.placement-banner');
const canvas = document.querySelector('#placement-confetti');
const replay = document.querySelector('#celebrate-again');
const status = document.querySelector('#celebration-status');
const motion = matchMedia('(prefers-reduced-motion: reduce)');
const context = canvas.getContext('2d');
const colors = ['#ec552d', '#a93418', '#202626', '#d4a837', '#788f8b'];
const entrance = 'cubic-bezier(.16,1,.3,1)';
let frame = 0;
let startedAt = 0;
let particles = [];
let animations = [];
let bounds;

function stopCelebration() {
  cancelAnimationFrame(frame);
  frame = 0;
  particles = [];
  animations.forEach(animation => animation.cancel());
  animations = [];
  context?.clearRect(0, 0, canvas.width, canvas.height);
}

function reveal(selector, keyframes, duration, delay) {
  const element = banner.querySelector(selector);
  animations.push(element.animate(keyframes, {duration, delay, easing: entrance}));
}

function drawConfetti(now) {
  const elapsed = (now - startedAt) / 1000;
  context.clearRect(0, 0, bounds.width, bounds.height);
  for (const particle of particles) {
    const age = elapsed - particle.delay;
    if (age < 0) continue;
    const x = particle.x + particle.vx * age + Math.sin(age * 3 + particle.phase) * 14;
    const y = particle.y + particle.vy * age + 100 * age * age;
    context.save();
    context.globalAlpha = Math.max(0, Math.min(1, (4.4 - elapsed) / .7));
    context.translate(x, y);
    context.rotate(particle.phase + age * particle.spin);
    context.scale(1, Math.cos(age * 5 + particle.phase) * .8);
    context.fillStyle = particle.color;
    context.fillRect(-particle.size / 2, -particle.size, particle.size, particle.size * 1.8);
    context.restore();
  }
  if (elapsed < 4.4) frame = requestAnimationFrame(drawConfetti);
  else stopCelebration();
}

function celebrate() {
  stopCelebration();
  if (motion.matches || document.hidden) return;
  reveal('h1 span:first-child', [
    {clipPath: 'inset(100% 0 0)', transform: 'translateY(16px)'},
    {clipPath: 'inset(0)', transform: 'translateY(0)'}
  ], 600, 0);
  reveal('h1 span:last-child', [
    {clipPath: 'inset(100% 0 0)', transform: 'translateY(16px)'},
    {clipPath: 'inset(0)', transform: 'translateY(0)'}
  ], 600, 160);
  reveal('.wafer-body', [{transform: 'rotate(-9deg) scale(.9)'}, {transform: 'rotate(0) scale(1)'}], 800, 400);
  reveal('.placement-arrow', [
    {transform: 'translate(-16px,16px) scale(.8)'},
    {transform: 'translate(0,0) scale(1)'}
  ], 500, 620);
  reveal('.wafer-sweep', [{transform: 'translate(-110px,110px)'}, {transform: 'translate(330px,-330px)'}], 1800, 700);
  reveal('.placement-destination', [{transform: 'translateY(8px)', opacity: .3}, {transform: 'translateY(0)', opacity: 1}], 450, 850);
  if (!context) return;
  bounds = banner.getBoundingClientRect();
  const ratio = Math.min(devicePixelRatio || 1, 2);
  canvas.width = Math.round(bounds.width * ratio);
  canvas.height = Math.round(bounds.height * ratio);
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  particles = Array.from({length: bounds.width < 600 ? 65 : 120}, () => {
    const isLeft = Math.random() < .5;
    return {
      x: isLeft ? 0 : bounds.width,
      y: bounds.height * .58,
      vx: (isLeft ? 1 : -1) * (90 + Math.random() * bounds.width * .25),
      vy: -190 - Math.random() * 160,
      size: 3 + Math.random() * 4,
      phase: Math.random() * Math.PI * 2,
      spin: (Math.random() - .5) * 7,
      delay: .7 + Math.random() * .35,
      color: colors[Math.floor(Math.random() * colors.length)]
    };
  });
  startedAt = performance.now();
  frame = requestAnimationFrame(drawConfetti);
}

replay.addEventListener('click', () => {
  status.textContent = 'Congratulations, Sivanesh, on joining Applied Materials!';
  celebrate();
});
motion.addEventListener('change', stopCelebration);
document.addEventListener('visibilitychange', () => { if (document.hidden) stopCelebration(); });
window.addEventListener('resize', stopCelebration);
window.addEventListener('pagehide', stopCelebration);
celebrate();
