const banner = document.querySelector('.placement-banner');
const canvas = document.querySelector('#placement-confetti');
const replay = document.querySelector('#celebrate-again');
const status = document.querySelector('#celebration-status');
const motion = matchMedia('(prefers-reduced-motion: reduce)');
const context = canvas.getContext('2d');
const colors = ['#ad2d41', '#2852a8', '#fff8e5', '#e98295', '#632731'];
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
    const y = particle.y + particle.vy * age + 135 * age * age;
    context.save();
    context.globalAlpha = Math.max(0, Math.min(1, (4.8 - elapsed) / .6));
    context.translate(x, y);
    context.rotate(particle.phase + age * particle.spin);
    context.scale(1, Math.cos(age * 5 + particle.phase) * .8);
    context.fillStyle = particle.color;
    if (particle.shape === 'circle') {
      context.beginPath();
      context.arc(0, 0, particle.size * .65, 0, Math.PI * 2);
      context.fill();
    } else {
      context.fillRect(-particle.size / 2, -particle.size, particle.size, particle.size * (particle.shape === 'ribbon' ? 4 : 1.8));
    }
    context.restore();
  }
  if (elapsed < 4.8) frame = requestAnimationFrame(drawConfetti);
  else stopCelebration();
}

function celebrate() {
  stopCelebration();
  if (motion.matches || document.hidden) return;
  reveal('h1 span:first-child', [
    {transform: 'translateY(24px) scale(.93)', opacity: .4},
    {transform: 'translateY(0) scale(1)', opacity: 1}
  ], 650, 0);
  reveal('h1 span:last-child', [
    {transform: 'scale(.8) rotate(-4deg)', opacity: .4},
    {transform: 'scale(1.04) rotate(1deg)', opacity: 1, offset: .65},
    {transform: 'scale(1) rotate(0)', opacity: 1}
  ], 800, 180);
  reveal('.party-flags', [{clipPath: 'inset(0 0 100%)'}, {clipPath: 'inset(0)'}], 700, 0);
  banner.querySelectorAll('.balloon').forEach((balloon, index) => {
    animations.push(balloon.animate([
      {transform: 'translateY(28px) rotate(-5deg)'},
      {transform: 'translateY(-8px) rotate(3deg)', offset: .6},
      {transform: 'translateY(0) rotate(0)'}
    ], {duration: 1800, delay: 100 + index * 90, easing: entrance}));
  });
  reveal('.placement-destination', [{transform: 'translateY(12px)', opacity: .4}, {transform: 'translateY(0)', opacity: 1}], 500, 450);
  if (!context) return;
  bounds = banner.getBoundingClientRect();
  const ratio = Math.min(devicePixelRatio || 1, 2);
  canvas.width = Math.round(bounds.width * ratio);
  canvas.height = Math.round(bounds.height * ratio);
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  particles = Array.from({length: bounds.width < 600 ? 150 : 260}, () => {
    const isLeft = Math.random() < .5;
    return {
      x: isLeft ? 0 : bounds.width,
      y: bounds.height * .86,
      vx: (isLeft ? 1 : -1) * (80 + Math.random() * bounds.width * .36),
      vy: -350 - Math.random() * 190,
      size: 4 + Math.random() * 5,
      phase: Math.random() * Math.PI * 2,
      spin: (Math.random() - .5) * 7,
      delay: .2 + Math.floor(Math.random() * 3) * .55 + Math.random() * .15,
      shape: ['paper', 'circle', 'ribbon'][Math.floor(Math.random() * 3)],
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
