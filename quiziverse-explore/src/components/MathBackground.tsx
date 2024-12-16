import React from 'react';
import Sketch from 'react-p5';
import p5Types from 'p5';

interface Symbol {
  x: number;
  y: number;
  value: string;
  size: number;
}

const MathBackground: React.FC = () => {
  const symbols = ['∑', '∫', '∏', '√', '∆', 'π', '±', '∞', '∂', '∇'];
  let mathSymbols: Symbol[] = [];
  let mouseX = 0;
  let mouseY = 0;

  const setup = (p5: p5Types, canvasParentRef: Element) => {
    p5.createCanvas(p5.windowWidth, p5.windowHeight).parent(canvasParentRef);
    for (let i = 0; i < 400; i++) {
      mathSymbols.push({
        x: p5.random(p5.width),
        y: p5.random(p5.height),
        value: symbols[Math.floor(p5.random(symbols.length))],
        size: p5.random(20, 40)
      });
    }
  };

  const draw = (p5: p5Types) => {
    p5.clear(0, 0, 0, 0);
    p5.textAlign(p5.CENTER, p5.CENTER);
    mouseX = p5.mouseX;
    mouseY = p5.mouseY;

    mathSymbols.forEach((symbol, index) => {
      const distance = p5.dist(mouseX, mouseY, symbol.x, symbol.y);
      const maxDistance = 150;
      
      if (distance < maxDistance) {
        const angle = p5.atan2(mouseY - symbol.y, mouseX - symbol.x);
        const force = (maxDistance - distance) / maxDistance;
        symbol.x -= p5.cos(angle) * force * 2;
        symbol.y -= p5.sin(angle) * force * 2;
      }

      p5.fill(0, 0, 0, 50);
      p5.textSize(symbol.size);
      p5.text(symbol.value, symbol.x, symbol.y);
    });

    // Keep symbols within canvas bounds
    mathSymbols = mathSymbols.map(symbol => ({
      ...symbol,
      x: p5.constrain(symbol.x, 0, p5.width),
      y: p5.constrain(symbol.y, 0, p5.height)
    }));
  };

  const windowResized = (p5: p5Types) => {
    p5.resizeCanvas(p5.windowWidth, p5.windowHeight);
  };

  return (
    <div className="fixed inset-0 -z-10">
      <Sketch setup={setup} draw={draw} windowResized={windowResized} />
    </div>
  );
};

export default MathBackground;
