const banner = document.querySelector('.placement-banner');
const canvas = document.querySelector('#placement-confetti');
const replay = document.querySelector('#celebrate-again');
const motion = matchMedia('(prefers-reduced-motion: reduce)');
const context = canvas.getContext('2d');
const colors = ['#f8ca72', '#fff9ed', '#86baff', '#f194a6', '#d3bbff'];
let frame = 0;
let startedAt = 0;
let particles = [];
let bounds;

function stopConfetti() {
  cancelAnimationFrame(frame);
  frame = 0;
  particles = [];
  context?.clearRect(0, 0, canvas.width, canvas.height);
}

function drawConfetti(now) {
  const elapsed = Math.min((now - startedAt) / 1000, 8);
  context.clearRect(0, 0, bounds.width, bounds.height);
  for (const particle of particles) {
    const age = elapsed - particle.delay;
    if (age < 0) continue;
    const x = particle.x + particle.vx * age + Math.sin(age * 3 + particle.phase) * 18;
    const y = particle.y + particle.vy * age + 54 * age * age;
    context.save();
    context.globalAlpha = Math.min(1, Math.max(0, 6.3 - age));
    context.translate(x, y);
    context.rotate(particle.phase + age * particle.spin);
    context.scale(1, Math.cos(age * 5 + particle.phase) * .8);
    context.fillStyle = particle.color;
    if (particle.isRound) {
      context.beginPath();
      context.arc(0, 0, particle.size / 2, 0, Math.PI * 2);
      context.fill();
    } else context.fillRect(-particle.size / 2, -particle.size, particle.size, particle.size * 1.8);
    context.restore();
  }
  if (elapsed < 7) frame = requestAnimationFrame(drawConfetti);
  else stopConfetti();
}

function celebrate() {
  stopConfetti();
  if (motion.matches || !context || document.hidden) return;
  bounds = banner.getBoundingClientRect();
  const ratio = Math.min(devicePixelRatio || 1, 2);
  canvas.width = Math.round(bounds.width * ratio);
  canvas.height = Math.round(bounds.height * ratio);
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  particles = Array.from({length: bounds.width < 600 ? 85 : 150}, () => {
    const isLeft = Math.random() < .5;
    return {
      x: isLeft ? 0 : bounds.width,
      y: bounds.height * .4 + Math.random() * 70,
      vx: (isLeft ? 1 : -1) * (70 + Math.random() * bounds.width * .28),
      vy: -180 - Math.random() * 200,
      size: 3 + Math.random() * 4,
      phase: Math.random() * Math.PI * 2,
      spin: (Math.random() - .5) * 7,
      delay: Math.random() * .65,
      color: colors[Math.floor(Math.random() * colors.length)],
      isRound: Math.random() < .25
    };
  });
  startedAt = performance.now();
  frame = requestAnimationFrame(drawConfetti);
}

replay.addEventListener('click', celebrate);
motion.addEventListener('change', stopConfetti);
document.addEventListener('visibilitychange', () => { if (document.hidden) stopConfetti(); });
window.addEventListener('resize', stopConfetti);
window.addEventListener('pagehide', stopConfetti);
celebrate();
