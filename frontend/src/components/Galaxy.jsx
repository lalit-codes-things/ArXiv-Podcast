import { useEffect, useRef } from "react";

const BASE_STAR_COUNT = 150;
const MAX_DEVICE_PIXEL_RATIO = 2;

function hslToRgb(hue, saturation, lightness) {
  const chroma = (1 - Math.abs(2 * lightness - 1)) * saturation;
  const segment = hue / 60;
  const second = chroma * (1 - Math.abs((segment % 2) - 1));
  const match = lightness - chroma / 2;
  let red = 0;
  let green = 0;
  let blue = 0;

  if (segment >= 0 && segment < 1) [red, green, blue] = [chroma, second, 0];
  else if (segment < 2) [red, green, blue] = [second, chroma, 0];
  else if (segment < 3) [red, green, blue] = [0, chroma, second];
  else if (segment < 4) [red, green, blue] = [0, second, chroma];
  else if (segment < 5) [red, green, blue] = [second, 0, chroma];
  else [red, green, blue] = [chroma, 0, second];

  return [
    Math.round((red + match) * 255),
    Math.round((green + match) * 255),
    Math.round((blue + match) * 255),
  ];
}

function makeStar(width, height, density) {
  const orbit = Math.random() * Math.hypot(width, height) * 0.55;
  const angle = Math.random() * Math.PI * 2;
  return {
    orbit,
    angle,
    x: width / 2 + Math.cos(angle) * orbit,
    y: height / 2 + Math.sin(angle) * orbit,
    radius: 0.4 + Math.random() * 1.8 * density,
    alpha: 0.25 + Math.random() * 0.75,
    twinkle: Math.random() * Math.PI * 2,
    drift: 0.12 + Math.random() * 0.45,
  };
}

export default function Galaxy({
  starSpeed = 0.5,
  density = 1,
  hueShift = 140,
  speed = 1,
  glowIntensity = 0.3,
  saturation = 0,
  mouseRepulsion = false,
  repulsionStrength = 2,
  twinkleIntensity = 0.3,
  rotationSpeed = 0.1,
  transparent = false,
}) {
  const canvasRef = useRef(null);
  const pointerRef = useRef({ x: 0, y: 0, active: false });

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d", { alpha: true });
    let animationFrame = 0;
    let stars = [];
    let width = 0;
    let height = 0;
    let pixelRatio = 1;

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      width = Math.max(rect.width, window.innerWidth, 1);
      height = Math.max(rect.height, window.innerHeight, 1);
      pixelRatio = Math.min(window.devicePixelRatio || 1, MAX_DEVICE_PIXEL_RATIO);
      canvas.width = Math.floor(width * pixelRatio);
      canvas.height = Math.floor(height * pixelRatio);
      context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);

      const viewportScale = Math.min(Math.max((width * height) / (1440 * 900), 0.65), 2.4);
      const starCount = Math.floor(BASE_STAR_COUNT * density * viewportScale);
      stars = Array.from({ length: starCount }, () => makeStar(width, height, density));
    };

    const handlePointerMove = (event) => {
      pointerRef.current = { x: event.clientX, y: event.clientY, active: true };
    };

    const handlePointerLeave = () => {
      pointerRef.current.active = false;
    };

    const draw = (time) => {
      context.clearRect(0, 0, width, height);
      if (!transparent) {
        context.fillStyle = "#120F17";
        context.fillRect(0, 0, width, height);
      }

      const [accentRed, accentGreen, accentBlue] = hslToRgb((120 + hueShift) % 360, saturation, 0.72);
      const centerX = width / 2;
      const centerY = height / 2;
      const rotation = (time / 100000) * rotationSpeed * speed;
      const pointer = pointerRef.current;

      context.save();
      context.globalCompositeOperation = "lighter";

      for (const star of stars) {
        star.angle += (starSpeed * star.drift * speed) / 6000;
        let x = centerX + Math.cos(star.angle + rotation) * star.orbit;
        let y = centerY + Math.sin(star.angle + rotation) * star.orbit * 0.58;

        if (mouseRepulsion && pointer.active) {
          const dx = x - pointer.x;
          const dy = y - pointer.y;
          const distance = Math.max(Math.hypot(dx, dy), 1);
          const influence = Math.max(0, 120 - distance) / 120;
          x += (dx / distance) * influence * repulsionStrength * 36;
          y += (dy / distance) * influence * repulsionStrength * 36;
        }

        const twinkle = 1 + Math.sin(time / 650 + star.twinkle) * twinkleIntensity;
        const alpha = Math.min(1, Math.max(0.05, star.alpha * twinkle));
        const radius = star.radius * twinkle;

        context.beginPath();
        context.fillStyle = `rgba(${accentRed}, ${accentGreen}, ${accentBlue}, ${alpha})`;
        context.shadowBlur = 14 * glowIntensity;
        context.shadowColor = `rgba(124, 255, 103, ${0.65 * glowIntensity})`;
        context.arc(x, y, radius, 0, Math.PI * 2);
        context.fill();
      }

      const coreGradient = context.createRadialGradient(centerX, centerY, 0, centerX, centerY, Math.min(width, height) * 0.42);
      coreGradient.addColorStop(0, "rgba(82, 39, 255, 0.18)");
      coreGradient.addColorStop(0.4, "rgba(124, 255, 103, 0.08)");
      coreGradient.addColorStop(1, "rgba(18, 15, 23, 0)");
      context.fillStyle = coreGradient;
      context.fillRect(0, 0, width, height);
      context.restore();

      animationFrame = requestAnimationFrame(draw);
    };

    resize();
    animationFrame = requestAnimationFrame(draw);
    window.addEventListener("resize", resize);
    window.addEventListener("pointermove", handlePointerMove, { passive: true });
    window.addEventListener("pointerleave", handlePointerLeave);

    return () => {
      cancelAnimationFrame(animationFrame);
      window.removeEventListener("resize", resize);
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerleave", handlePointerLeave);
    };
  }, [density, glowIntensity, hueShift, mouseRepulsion, repulsionStrength, rotationSpeed, saturation, speed, starSpeed, transparent, twinkleIntensity]);

  return <canvas ref={canvasRef} className="galaxy-canvas" />;
}
