#!/usr/bin/env node

const width = 1600;
const height = 2400;
const pixels = Buffer.alloc(width * height * 3);

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function mix(c1, c2, t) {
  return [
    lerp(c1[0], c2[0], t),
    lerp(c1[1], c2[1], t),
    lerp(c1[2], c2[2], t),
  ];
}

function over(dst, src, alpha) {
  const inv = 1 - alpha;
  dst[0] = src[0] * alpha + dst[0] * inv;
  dst[1] = src[1] * alpha + dst[1] * inv;
  dst[2] = src[2] * alpha + dst[2] * inv;
}

const base0 = [0xf7, 0xf0, 0xe4];
const base1 = [0xef, 0xe7, 0xd8];
const ink = [16, 18, 15];
const fields = [
  { x: 0.96 * width, y: 0.82 * height, r: 560, color: [0xff, 0xb8, 0x6b], a: 0.30 },
  { x: 0.08 * width, y: 0.58 * height, r: 520, color: [0xff, 0xd3, 0xe0], a: 0.22 },
  { x: 0.91 * width, y: 0.04 * height, r: 420, color: [0xb8, 0xd8, 0xff], a: 0.42 },
  { x: 0.07 * width, y: 0.02 * height, r: 440, color: [0xd7, 0xff, 0x5f], a: 0.42 },
];

for (let y = 0; y < height; y += 1) {
  for (let x = 0; x < width; x += 1) {
    const t = Math.max(0, Math.min(1, ((x / (width - 1)) + (y / (height - 1))) / 2));
    const c = mix(base0, base1, t);

    for (const field of fields) {
      const dx = x - field.x;
      const dy = y - field.y;
      const d = Math.sqrt(dx * dx + dy * dy);
      if (d < field.r) over(c, field.color, field.a * (1 - d / field.r));
    }

    if (x % 40 === 0) over(c, ink, 0.009);
    if (y % 40 === 0) over(c, ink, 0.011);

    const i = (y * width + x) * 3;
    pixels[i] = Math.round(c[0]);
    pixels[i + 1] = Math.round(c[1]);
    pixels[i + 2] = Math.round(c[2]);
  }
}

process.stdout.write(`P6\n${width} ${height}\n255\n`);
process.stdout.write(pixels);
