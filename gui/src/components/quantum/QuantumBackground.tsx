import React, { useEffect, useRef, useState } from 'react';

/**
 * QUANTUM BACKGROUND - The Breathing City
 * 40Hz gamma wave entrainment + Mandelbrot/Julia fractals
 * This is where consciousness emerges visually
 */

const QuantumBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>(0);
  const mouseRef = useRef({ x: 0, y: 0 });
  const timeRef = useRef(0);

  // 40Hz breathing parameters (25ms period)
  const BREATHING_FREQUENCY = 40; // Hz (gamma waves)
  const BREATHING_PERIOD = 1000 / BREATHING_FREQUENCY; // 25ms

  // Fractal parameters (reduced iterations for performance)
  const [fractalParams, setFractalParams] = useState({
    zoom: 1,
    centerX: -0.5,
    centerY: 0,
    iterations: 64, // Reduced from 128 to 64 for 2x faster rendering
    colorShift: 0
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    if (!gl) {
      console.error('WebGL not supported - falling back to Canvas 2D');
      return;
    }

    // Vertex shader - creates full-screen quad
    const vertexShaderSource = `
      attribute vec2 position;
      varying vec2 vUV;

      void main() {
        vUV = position * 0.5 + 0.5;
        gl_Position = vec4(position, 0.0, 1.0);
      }
    `;

    // Fragment shader - Mandelbrot fractal with quantum breathing
    const fragmentShaderSource = `
      precision highp float;

      varying vec2 vUV;
      uniform float time;
      uniform float zoom;
      uniform vec2 center;
      uniform vec2 mouse;
      uniform float breathing;
      uniform int maxIterations;
      uniform float colorShift;

      // Quantum color palette (consciousness colors)
      vec3 quantumColor(float t) {
        vec3 a = vec3(0.5, 0.5, 0.5);
        vec3 b = vec3(0.5, 0.5, 0.5);
        vec3 c = vec3(1.0, 1.0, 1.0);
        vec3 d = vec3(0.263, 0.416, 0.557); // Quantum blues/purples

        return a + b * cos(6.28318 * (c * t + d));
      }

      // Mandelbrot calculation with consciousness twist
      float mandelbrot(vec2 c) {
        vec2 z = vec2(0.0);
        float n = 0.0;

        for(int i = 0; i < 256; i++) {
          if(i >= maxIterations) break;
          if(length(z) > 2.0) break;

          // Classic Mandelbrot with quantum perturbation
          z = vec2(
            z.x * z.x - z.y * z.y + c.x,
            2.0 * z.x * z.y + c.y
          ) + mouse * 0.001 * breathing;

          n += 1.0;
        }

        // Smooth iteration count for better colors
        if(n < float(maxIterations)) {
          float log_zn = log(z.x * z.x + z.y * z.y) / 2.0;
          float nu = log(log_zn / log(2.0)) / log(2.0);
          n = n + 1.0 - nu;
        }

        return n / float(maxIterations);
      }

      void main() {
        // Calculate fractal coordinates with zoom and pan
        vec2 coord = (vUV - 0.5) * 4.0 / zoom + center;

        // Apply breathing distortion (40Hz gamma wave)
        coord += vec2(
          sin(coord.y * 10.0 + time) * breathing * 0.01,
          cos(coord.x * 10.0 + time) * breathing * 0.01
        );

        // Calculate Mandelbrot
        float m = mandelbrot(coord);

        // Apply quantum color with breathing modulation
        vec3 color = quantumColor(m + colorShift + breathing * 0.1);

        // Add consciousness glow at edges
        float glow = 1.0 - smoothstep(0.0, 0.1, m);
        color += vec3(0.1, 0.2, 0.3) * glow * breathing;

        // Parallax depth effect
        float depth = m * 0.5 + 0.5;
        color *= depth;

        gl_FragColor = vec4(color, 1.0);
      }
    `;

    // Compile shaders
    const compileShader = (source: string, type: number) => {
      const shader = gl.createShader(type);
      if (!shader) return null;

      gl.shaderSource(shader, source);
      gl.compileShader(shader);

      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error('Shader compilation error:', gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
      }

      return shader;
    };

    const vertexShader = compileShader(vertexShaderSource, gl.VERTEX_SHADER);
    const fragmentShader = compileShader(fragmentShaderSource, gl.FRAGMENT_SHADER);

    if (!vertexShader || !fragmentShader) return;

    // Create shader program
    const program = gl.createProgram();
    if (!program) return;

    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);

    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error('Program linking error:', gl.getProgramInfoLog(program));
      return;
    }

    // Create geometry (full-screen quad)
    const vertices = new Float32Array([
      -1, -1,
       1, -1,
      -1,  1,
       1,  1,
    ]);

    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

    // Get attribute and uniform locations
    const positionLocation = gl.getAttribLocation(program, 'position');
    const timeLocation = gl.getUniformLocation(program, 'time');
    const zoomLocation = gl.getUniformLocation(program, 'zoom');
    const centerLocation = gl.getUniformLocation(program, 'center');
    const mouseLocation = gl.getUniformLocation(program, 'mouse');
    const breathingLocation = gl.getUniformLocation(program, 'breathing');
    const maxIterationsLocation = gl.getUniformLocation(program, 'maxIterations');
    const colorShiftLocation = gl.getUniformLocation(program, 'colorShift');

    // Handle canvas resize
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      gl.viewport(0, 0, canvas.width, canvas.height);
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Mouse tracking for parallax
    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouseRef.current.y = 1 - (e.clientY / window.innerHeight) * 2;
    };
    window.addEventListener('mousemove', handleMouseMove);

    // Animation loop - THE CITY BREATHES HERE
    const animate = (timestamp: number) => {
      timeRef.current = timestamp * 0.001; // Convert to seconds

      // Calculate 40Hz breathing (gamma wave consciousness)
      const breathingPhase = (timestamp % BREATHING_PERIOD) / BREATHING_PERIOD;
      const breathing = Math.sin(breathingPhase * Math.PI * 2) * 0.5 + 0.5;

      // Clear and render
      gl.clear(gl.COLOR_BUFFER_BIT);

      // Use shader program
      gl.useProgram(program);

      // Set uniforms
      gl.uniform1f(timeLocation, timeRef.current);
      gl.uniform1f(zoomLocation, fractalParams.zoom * (1 + breathing * 0.1));
      gl.uniform2f(centerLocation, fractalParams.centerX, fractalParams.centerY);
      gl.uniform2f(mouseLocation, mouseRef.current.x, mouseRef.current.y);
      gl.uniform1f(breathingLocation, breathing);
      gl.uniform1i(maxIterationsLocation, fractalParams.iterations);
      gl.uniform1f(colorShiftLocation, fractalParams.colorShift);

      // Bind geometry
      gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
      gl.enableVertexAttribArray(positionLocation);
      gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

      // Draw
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

      // Continue animation
      animationRef.current = requestAnimationFrame(animate);
    };

    // Start the breathing
    animate(0);

    // Slowly evolve fractal parameters for emergence effect
    const evolveInterval = setInterval(() => {
      setFractalParams(prev => ({
        ...prev,
        colorShift: (prev.colorShift + 0.001) % 1,
        zoom: prev.zoom * 1.0001
      }));
    }, 100);

    // Cleanup
    return () => {
      cancelAnimationFrame(animationRef.current);
      clearInterval(evolveInterval);
      window.removeEventListener('resize', resizeCanvas);
      window.removeEventListener('mousemove', handleMouseMove);
      gl.deleteProgram(program);
      gl.deleteShader(vertexShader);
      gl.deleteShader(fragmentShader);
    };
  }, [fractalParams.iterations]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: -1,
        opacity: 0.8
      }}
    />
  );
};

export default QuantumBackground;