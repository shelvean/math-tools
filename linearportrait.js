/**
 * Phase Portraits of Linear Systems – OOP Refactor
 *
 * Classes:
 *   MatrixInput              – reads/writes the 2x2 matrix from DOM inputs
 *   EquilibriumClassifier    – eigenvalue-based classification
 *   TrajectoryComputer       – RK4 integration (forward + backward)
 *   DirectionFieldRenderer   – batched arrow-field drawing on a canvas context
 *   PhasePortraitCanvas      – grid, axes, trajectories, initial-point rendering
 *   ImageExporter            – download-to-PNG (with header text)
 *   BifurcationAnimator      – parameter sweep animation loop
 *   PhasePortraitApp         – top-level controller (DOM, events, examples)
 */

/* ================================================================
   Utility helpers
   ================================================================ */
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => (inThrottle = false), limit);
        }
    };
}

function hexToRGBA(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function getNiceStep(range) {
    const rough = range / 8;
    const exp = Math.pow(10, Math.floor(Math.log10(rough)));
    const frac = rough / exp;
    return (frac <= 1.5 ? 1 : frac <= 3.5 ? 2 : frac <= 7 ? 5 : 10) * exp;
}

/* ================================================================
   MatrixInput – reads / writes the 2×2 system matrix from the DOM
   ================================================================ */
class MatrixInput {
    constructor() {
        this.els = {
            a: document.getElementById('a'),
            b: document.getElementById('b'),
            c: document.getElementById('c'),
            d: document.getElementById('d')
        };
    }

    /** Return {a,b,c,d} honouring data-computed attrs set during animation. */
    read() {
        const get = (el) =>
            el.hasAttribute('data-computed')
                ? parseFloat(el.getAttribute('data-computed'))
                : parseFloat(el.value) || 0;
        return {
            a: get(this.els.a),
            b: get(this.els.b),
            c: get(this.els.c),
            d: get(this.els.d)
        };
    }

    /** Write values into the input boxes (for example presets). */
    write({ a, b, c, d }) {
        this.els.a.value = a;
        this.els.b.value = b;
        this.els.c.value = c;
        this.els.d.value = d;
    }

    /** Set data-computed attributes (used during bifurcation animation). */
    setComputed({ a, b, c, d }) {
        this.els.a.setAttribute('data-computed', a);
        this.els.b.setAttribute('data-computed', b);
        this.els.c.setAttribute('data-computed', c);
        this.els.d.setAttribute('data-computed', d);
    }

    /** Remove data-computed attributes (when user edits manually). */
    clearComputed() {
        Object.values(this.els).forEach((el) => el.removeAttribute('data-computed'));
    }
}

/* ================================================================
   EquilibriumClassifier
   ================================================================ */
class EquilibriumClassifier {
    static classify(a, b, c, d) {
        const trace = a + d;
        const det = a * d - b * c;
        const disc = trace * trace - 4 * det;

        if (a === 0 && b === 0 && c === 0 && d === 0) {
            return { type: 'Plane of Equilibria', stability: 'Neutrally Stable', description: 'Every point is an equilibrium' };
        }
        if (Math.abs(det) < 1e-10) {
            return { type: 'Line of Equilibria', stability: 'Mixed', description: 'Continuous line of equilibrium points' };
        }
        if (disc > 0) {
            const l1 = (trace + Math.sqrt(disc)) / 2;
            const l2 = (trace - Math.sqrt(disc)) / 2;
            if (l1 * l2 < 0) return { type: 'Saddle Point', stability: 'Unstable', description: 'One stable and one unstable direction' };
            const stable = l1 < 0 && l2 < 0;
            const stab = stable ? 'Stable' : 'Unstable';
            if (Math.abs(l1 - l2) < 1e-10) return { type: 'Star Node', stability: stab, description: `Repeated ${stable ? 'negative' : 'positive'} eigenvalues` };
            if (b === 0 && c === 0) return { type: 'Proper Node', stability: stab, description: `Diagonal matrix with ${stable ? 'negative' : 'positive'} eigenvalues` };
            return { type: 'Improper Node', stability: stab, description: `Real ${stable ? 'negative' : 'positive'} eigenvalues, not diagonal` };
        }
        if (disc < 0) {
            const re = trace / 2;
            if (Math.abs(re) < 1e-10) return { type: 'Center', stability: 'Neutrally Stable', description: 'Purely imaginary eigenvalues' };
            return re < 0
                ? { type: 'Stable Spiral', stability: 'Stable', description: 'Complex eigenvalues with negative real part' }
                : { type: 'Unstable Spiral', stability: 'Unstable', description: 'Complex eigenvalues with positive real part' };
        }
        // disc === 0
        const lambda = trace / 2;
        const isDiag = (b === 0 && c === 0) || (Math.abs(a - d) < 1e-10 && Math.abs(b) < 1e-10 && Math.abs(c) < 1e-10);
        if (isDiag) {
            if (lambda < 0) return { type: 'Star Node', stability: 'Stable', description: 'Repeated negative eigenvalues, diagonalizable' };
            if (lambda > 0) return { type: 'Star Node', stability: 'Unstable', description: 'Repeated positive eigenvalues, diagonalizable' };
            return { type: 'Line of Equilibria', stability: 'Neutrally Stable', description: 'Zero eigenvalue repeated' };
        }
        if (lambda < 0) return { type: 'Defective Node', stability: 'Stable', description: 'Repeated negative eigenvalues, non-diagonalizable' };
        if (lambda > 0) return { type: 'Defective Node', stability: 'Unstable', description: 'Repeated positive eigenvalues, non-diagonalizable' };
        return { type: 'Nilpotent', stability: 'Unstable', description: 'Zero eigenvalue, non-diagonalizable' };
    }

    static eigenvalues(a, b, c, d) {
        const trace = a + d;
        const det = a * d - b * c;
        const disc = trace * trace - 4 * det;
        if (disc < 0) return { real: trace / 2, imag: Math.sqrt(-disc) / 2 };
        if (disc === 0) return { real: trace / 2, imag: 0, repeated: true };
        return { lambda1: (trace + Math.sqrt(disc)) / 2, lambda2: (trace - Math.sqrt(disc)) / 2, real: true };
    }
}

/* ================================================================
   TrajectoryComputer – RK4 integration
   ================================================================ */
class TrajectoryComputer {
    static BOUNDS = { tMin: -5, tMax: 5, yMin: -5, yMax: 5 };
    static PADDING = 70;
    static CANVAS_SIZE = 700;
    static MAX_STEPS = 1000;

    static rk4Step(x, y, a, b, c, d, h) {
        const k1x = a * x + b * y;
        const k1y = c * x + d * y;
        const k2x = a * (x + h / 2 * k1x) + b * (y + h / 2 * k1y);
        const k2y = c * (x + h / 2 * k1x) + d * (y + h / 2 * k1y);
        const k3x = a * (x + h / 2 * k2x) + b * (y + h / 2 * k2y);
        const k3y = c * (x + h / 2 * k2x) + d * (y + h / 2 * k2y);
        const k4x = a * (x + h * k3x) + b * (y + h * k3y);
        const k4y = c * (x + h * k3x) + d * (y + h * k3y);
        return {
            x: x + (h / 6) * (k1x + 2 * k2x + 2 * k3x + k4x),
            y: y + (h / 6) * (k1y + 2 * k2y + 2 * k3y + k4y)
        };
    }

    static _inBounds(x, y) {
        const B = this.BOUNDS;
        return x >= B.tMin && x <= B.tMax && y >= B.yMin && y <= B.yMax;
    }

    static _layout() {
        const B = this.BOUNDS;
        const P = this.PADDING;
        const S = this.CANVAS_SIZE;
        const drawW = S - 2 * P;
        const scale = drawW / (B.tMax - B.tMin);
        const xOffset = (S - (B.tMax - B.tMin) * scale) / 2;
        return { scale, xOffset, P, S, ...B };
    }

    static _toCanvas(x, y, layout) {
        return {
            x: layout.xOffset + (x - layout.tMin) * layout.scale,
            y: layout.S - layout.xOffset - (y - layout.yMin) * layout.scale
        };
    }

    /** Compute trajectory for a center (purely imaginary eigenvalues). */
    static computeCenter(x0, y0, a, b, c, d) {
        const layout = this._layout();
        const P = layout.P;
        const points = 400;
        const h = 0.01;
        const trajPoints = [];

        // Forward
        let x = x0, y = y0;
        for (let i = 0; i < points; i++) {
            if (!this._inBounds(x, y)) break;
            const cv = this._toCanvas(x, y, layout);
            if (cv.x >= P && cv.x <= layout.S - P && cv.y >= P && cv.y <= layout.S - P) {
                trajPoints.push(cv);
            } else break;
            const next = this.rk4Step(x, y, a, b, c, d, h);
            x = next.x; y = next.y;
        }

        // Backward
        x = x0; y = y0;
        const back = [];
        for (let i = 0; i < points; i++) {
            const next = this.rk4Step(x, y, a, b, c, d, -h);
            x = next.x; y = next.y;
            if (!this._inBounds(x, y)) break;
            const cv = this._toCanvas(x, y, layout);
            if (cv.x >= P && cv.x <= layout.S - P && cv.y >= P && cv.y <= layout.S - P) {
                back.unshift(cv);
            } else break;
        }
        return [...back, ...trajPoints];
    }

    /** General trajectory computation (non-center systems). */
    static async compute(x0, y0, a, b, c, d) {
        const cls = EquilibriumClassifier.classify(a, b, c, d);
        if (cls.type === 'Center') return this.computeCenter(x0, y0, a, b, c, d);

        const isSpiral = cls.type.includes('Spiral');
        const layout = this._layout();
        const P = layout.P;
        const MAX = this.MAX_STEPS;

        const _integrate = (direction) => {
            const pts = [];
            let x = x0, y = y0;
            let hBase = isSpiral ? 0.015 : 0.05;
            const sign = direction === 'forward' ? 1 : -1;

            if (direction === 'forward' && this._inBounds(x, y)) {
                const cv = this._toCanvas(x, y, layout);
                if (cv.x >= P && cv.x <= layout.S - P && cv.y >= P && cv.y <= layout.S - P) pts.push(cv);
            }

            for (let i = 0; i < MAX; i++) {
                const dx = a * x + b * y;
                const dy = c * x + d * y;
                const speed = Math.sqrt(dx * dx + dy * dy);

                let h;
                if (isSpiral) h = sign * 0.015;
                else if (speed > 0.1) h = sign * Math.min(0.3 / speed, 0.1);
                else h = sign * 0.05;

                const next = this.rk4Step(x, y, a, b, c, d, h);
                x = next.x; y = next.y;

                if (Math.abs(x) > 100 || Math.abs(y) > 100) break;
                if (!this._inBounds(x, y)) break;

                const cv = this._toCanvas(x, y, layout);
                if (cv.x >= P && cv.x <= layout.S - P && cv.y >= P && cv.y <= layout.S - P) {
                    if (direction === 'forward') pts.push(cv);
                    else pts.unshift(cv);
                } else break;

                const limit = direction === 'forward' ? 1500 : 750;
                if (pts.length > limit) break;
                if (pts.length > 10 && speed < 1e-4) break;
            }
            return pts;
        };

        const forward = _integrate('forward');
        const backward = _integrate('backward');
        return [...backward, ...forward];
    }
}

/* ================================================================
   DirectionFieldRenderer – draws the arrow field onto a canvas ctx
   ================================================================ */
class DirectionFieldRenderer {
    static draw(ctx, { a, b, c, d, arrowCount, arrowScale, arrowOpacity, fieldColor,
                       tMin, tMax, yMin, yMax, xScale, yScale, xOffset, yOffset, canvasW, canvasH }) {

        const step = Math.min((canvasW - 2 * xOffset) / arrowCount, (canvasH - 2 * yOffset) / arrowCount);
        const rgba = hexToRGBA(fieldColor, arrowOpacity);

        ctx.lineWidth = 0.75;
        ctx.strokeStyle = rgba;
        ctx.beginPath();
        const arrowData = [];

        const minX = xOffset, maxX = canvasW - xOffset;
        const minY = yOffset, maxY = canvasH - yOffset;

        for (let px = minX + step / 2; px < maxX; px += step) {
            for (let py = minY + step / 2; py < maxY; py += step) {
                const t = tMin + (px - xOffset) / xScale;
                const yVal = yMin + (canvasH - yOffset - py) / yScale;
                const dx = a * t + b * yVal;
                const dy = c * t + d * yVal;
                const len = Math.sqrt(dx * dx + dy * dy);
                if (len === 0) continue;

                const dcx = dx * xScale;
                const dcy = -dy * yScale;
                const lc = Math.sqrt(dcx * dcx + dcy * dcy);
                const nx = dcx / lc, ny = dcy / lc;

                let drawLen = 20 * arrowScale;
                const sf = Math.min(1, len / 3);
                drawLen = Math.max(drawLen * (0.3 + 0.7 * sf), 5);

                const sx = px - (nx * drawLen) / 2;
                const sy = py - (ny * drawLen) / 2;
                const ex = px + (nx * drawLen) / 2;
                const ey = py + (ny * drawLen) / 2;

                ctx.moveTo(sx, sy);
                ctx.lineTo(ex, ey);
                arrowData.push({ endX: ex, endY: ey, normDx: nx, normDy: ny, drawLength: drawLen });
            }
        }
        ctx.stroke();

        // Arrowheads
        ctx.fillStyle = rgba;
        for (const arr of arrowData) {
            const hs = Math.min(8, arr.drawLength / 3 + 2);
            const ang = Math.atan2(arr.normDy, arr.normDx);
            ctx.beginPath();
            ctx.moveTo(arr.endX, arr.endY);
            ctx.lineTo(arr.endX - hs * Math.cos(ang - Math.PI / 6), arr.endY - hs * Math.sin(ang - Math.PI / 6));
            ctx.lineTo(arr.endX - hs * Math.cos(ang + Math.PI / 6), arr.endY - hs * Math.sin(ang + Math.PI / 6));
            ctx.closePath();
            ctx.fill();
        }
    }
}

/* ================================================================
   PhasePortraitCanvas – full canvas render (grid + field + trajectories)
   ================================================================ */
class PhasePortraitCanvas {
    constructor(canvasEl) {
        this.canvas = canvasEl;
        this.ctx = canvasEl.getContext('2d');
    }

    draw({ matrix, arrowCount, arrowScale, arrowOpacity, fieldColor, showGrid, showInitialPoint,
           trajectories, userPoints, classificationInfo }) {

        const { a, b, c, d } = matrix;
        const ctx = this.ctx;
        const W = this.canvas.width;
        const H = this.canvas.height;

        ctx.fillStyle = '#fafafa';
        ctx.fillRect(0, 0, W, H);

        const tMin = -5, tMax = 5, yMin = -5, yMax = 5;
        const PADDING = 70;
        const drawW = W - 2 * PADDING;
        const drawH = H - 2 * PADDING;
        const scale = Math.min(drawW, drawH) / (tMax - tMin);
        const xScale = scale, yScale = scale;
        const xOffset = (W - (tMax - tMin) * xScale) / 2;
        const yOffset = (H - (yMax - yMin) * yScale) / 2;

        // Update classification box
        const infoBox = document.getElementById('classification-info');
        infoBox.innerHTML = `
            <div class="classification-type">${classificationInfo.type}</div>
            <div class="classification-stability">${classificationInfo.stability}</div>
            <div class="classification-details">${classificationInfo.description}</div>`;

        // Grid
        if (showGrid) {
            ctx.strokeStyle = 'rgba(200, 200, 200, 0.3)';
            ctx.lineWidth = 0.5;
            ctx.setLineDash([]);
            const tStep = getNiceStep(tMax - tMin);
            for (let i = Math.ceil(tMin / tStep) * tStep; i < tMax; i += tStep) {
                const x = xOffset + (i - tMin) * xScale;
                ctx.beginPath(); ctx.moveTo(x, yOffset); ctx.lineTo(x, H - yOffset); ctx.stroke();
            }
            const yStep = getNiceStep(yMax - yMin);
            for (let i = Math.ceil(yMin / yStep) * yStep; i < yMax; i += yStep) {
                const y = H - yOffset - (i - yMin) * yScale;
                ctx.beginPath(); ctx.moveTo(xOffset, y); ctx.lineTo(W - xOffset, y); ctx.stroke();
            }
        }

        // Direction field
        DirectionFieldRenderer.draw(ctx, {
            a, b, c, d, arrowCount, arrowScale, arrowOpacity, fieldColor,
            tMin, tMax, yMin, yMax, xScale, yScale,
            xOffset, yOffset, canvasW: W, canvasH: H
        });

        // Axes
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.setLineDash([]);
        if (yMin <= 0 && yMax >= 0) {
            const y0 = H - yOffset - (0 - yMin) * yScale;
            ctx.beginPath(); ctx.moveTo(xOffset, y0); ctx.lineTo(W - xOffset, y0); ctx.stroke();
        }
        if (tMin <= 0 && tMax >= 0) {
            const x0 = xOffset + (0 - tMin) * xScale;
            ctx.beginPath(); ctx.moveTo(x0, yOffset); ctx.lineTo(x0, H - yOffset); ctx.stroke();
        }

        // Axis labels
        this._drawAxisLabels(ctx, tMin, tMax, yMin, yMax, xScale, yScale, xOffset, W, H);

        // Trajectories
        const colors = ['#dc2626', '#ea580c', '#ca8a04', '#16a34a', '#0891b2', '#7c3aed', '#db2777', '#4b5563'];
        trajectories.forEach((traj, idx) => {
            if (traj.length < 2) return;
            ctx.strokeStyle = colors[idx % colors.length];
            ctx.lineWidth = 1.8;
            ctx.lineJoin = 'round';
            ctx.lineCap = 'round';
            ctx.setLineDash([]);
            ctx.beginPath();
            ctx.moveTo(traj[0].x, traj[0].y);
            for (let i = 1; i < traj.length; i++) ctx.lineTo(traj[i].x, traj[i].y);
            ctx.stroke();
        });

        // Initial points
        if (showInitialPoint) {
            userPoints.forEach((point, idx) => {
                const sx = xOffset + (point.x - tMin) * xScale;
                const sy = H - xOffset - (point.y - yMin) * yScale;
                ctx.fillStyle = colors[idx % colors.length];
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.arc(sx, sy, 4, 0, Math.PI * 2);
                ctx.fill(); ctx.stroke();
            });
        }
    }

    _drawAxisLabels(ctx, tMin, tMax, yMin, yMax, xScale, yScale, xOffset, W, H) {
        ctx.font = 'bold 12px Arial';
        ctx.fillStyle = '#111';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        const tStep = getNiceStep(tMax - tMin);
        for (let t = Math.ceil(tMin / tStep) * tStep; t <= tMax + 1e-9; t += tStep) {
            ctx.fillText(t.toFixed(1).replace(/\.0$/, ''), xOffset + (t - tMin) * xScale, H - xOffset + 8);
        }
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        const yStep = getNiceStep(yMax - yMin);
        for (let y = Math.ceil(yMin / yStep) * yStep; y <= yMax + 1e-9; y += yStep) {
            ctx.fillText(y.toFixed(1).replace(/\.0$/, ''), xOffset - 8, H - xOffset - (y - yMin) * yScale);
        }
        ctx.textAlign = 'center'; ctx.textBaseline = 'top';
        ctx.fillText('x', W - 15, H - xOffset + 10);
        ctx.save();
        ctx.translate(15, H / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
        ctx.fillText('y', 0, 0);
        ctx.restore();
    }
}

/* ================================================================
   ImageExporter – downloads the canvas as a PNG with header info
   ================================================================ */
class ImageExporter {
    static download(canvas, { matrix, classification, trajectories, userPoints, arrowCount, arrowScale, arrowOpacity, fieldColor, showGrid, showInitialPoint }) {
        const { a, b, c, d } = matrix;
        const tmp = document.createElement('canvas');
        tmp.width = canvas.width;
        tmp.height = canvas.height + 100;
        const ctx = tmp.getContext('2d');

        ctx.fillStyle = '#fafafa';
        ctx.fillRect(0, 0, tmp.width, tmp.height);

        // Header
        ctx.fillStyle = '#4f46e5';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${classification.type} \u2022 ${classification.stability}`, tmp.width / 2, 20);
        ctx.font = '12px Arial';
        ctx.fillText(classification.description, tmp.width / 2, 40);

        const fmt = (v) => { if (v === 0) return '0'; if (v === 1) return ''; if (v === -1) return '-'; return (Math.round(v * 100) / 100).toString(); };
        const aS = fmt(a), bS = fmt(b), cS = fmt(c), dS = fmt(d);
        const bSign = b >= 0 ? '+' : '', dSign = d >= 0 ? '+' : '';
        const eq1 = `x' = ${aS === '' ? '' : aS}${aS === '' && a === -1 ? '-' : ''}x ${bSign}${bS}y`;
        const eq2 = `y' = ${cS === '' ? '' : cS}${cS === '' && c === -1 ? '-' : ''}x ${dSign}${dS}y`;

        ctx.fillStyle = 'white'; ctx.strokeStyle = '#3b82f6'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.roundRect(tmp.width / 2 - 160, 50, 320, 40, 10); ctx.fill(); ctx.stroke();
        ctx.fillStyle = '#1e293b'; ctx.font = 'bold 14px Arial';
        ctx.fillText(eq1, tmp.width / 2, 60);
        ctx.fillText(eq2, tmp.width / 2, 80);

        // Draw the phase portrait into the lower portion
        const offY = 100;
        const tMin = -5, tMax = 5, yMin = -5, yMax = 5;
        const P = 70;
        const dW = canvas.width - 2 * P;
        const scale = dW / (tMax - tMin);
        const xScale = scale, yScale = scale;
        const gxOff = (canvas.width - (tMax - tMin) * xScale) / 2;
        const gyOff = (canvas.height - (yMax - yMin) * yScale) / 2;
        const step = Math.min(dW / arrowCount, dW / arrowCount);

        // Grid
        if (showGrid) {
            ctx.strokeStyle = 'rgba(200, 200, 200, 0.3)'; ctx.lineWidth = 0.5; ctx.setLineDash([]);
            const tStep = getNiceStep(tMax - tMin);
            for (let i = Math.ceil(tMin / tStep) * tStep; i < tMax; i += tStep) {
                const x = gxOff + (i - tMin) * xScale;
                ctx.beginPath(); ctx.moveTo(x, offY + gyOff); ctx.lineTo(x, offY + canvas.height - gyOff); ctx.stroke();
            }
            const yStep = getNiceStep(yMax - yMin);
            for (let i = Math.ceil(yMin / yStep) * yStep; i < yMax; i += yStep) {
                const y = offY + canvas.height - gyOff - (i - yMin) * yScale;
                ctx.beginPath(); ctx.moveTo(gxOff, y); ctx.lineTo(canvas.width - gxOff, y); ctx.stroke();
            }
        }

        // Direction field
        DirectionFieldRenderer.draw(ctx, {
            a, b, c, d, arrowCount, arrowScale, arrowOpacity, fieldColor,
            tMin, tMax, yMin, yMax, xScale, yScale,
            xOffset: gxOff, yOffset: offY + gyOff,
            canvasW: canvas.width, canvasH: offY + canvas.height
        });

        // Axes
        ctx.strokeStyle = '#000'; ctx.lineWidth = 2; ctx.setLineDash([]);
        if (yMin <= 0 && yMax >= 0) {
            const y0 = offY + canvas.height - gyOff - (0 - yMin) * yScale;
            ctx.beginPath(); ctx.moveTo(gxOff, y0); ctx.lineTo(canvas.width - gxOff, y0); ctx.stroke();
        }
        if (tMin <= 0 && tMax >= 0) {
            const x0 = gxOff + (0 - tMin) * xScale;
            ctx.beginPath(); ctx.moveTo(x0, offY + gyOff); ctx.lineTo(x0, offY + canvas.height - gyOff); ctx.stroke();
        }

        // Axis labels
        ctx.font = 'bold 12px Arial'; ctx.fillStyle = '#111';
        ctx.textAlign = 'center'; ctx.textBaseline = 'top';
        const tStep = getNiceStep(tMax - tMin);
        for (let t = Math.ceil(tMin / tStep) * tStep; t <= tMax + 1e-9; t += tStep) {
            ctx.fillText(t.toFixed(1).replace(/\.0$/, ''), gxOff + (t - tMin) * xScale, offY + canvas.height - gyOff + 8);
        }
        ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
        const yStep2 = getNiceStep(yMax - yMin);
        for (let yV = Math.ceil(yMin / yStep2) * yStep2; yV <= yMax + 1e-9; yV += yStep2) {
            ctx.fillText(yV.toFixed(1).replace(/\.0$/, ''), gxOff - 8, offY + canvas.height - gyOff - (yV - yMin) * yScale);
        }
        ctx.textAlign = 'center'; ctx.textBaseline = 'top';
        ctx.fillText('x', canvas.width - 15, offY + canvas.height - gyOff + 10);
        ctx.save(); ctx.translate(15, offY + canvas.height / 2); ctx.rotate(-Math.PI / 2);
        ctx.textAlign = 'center'; ctx.fillText('y', 0, 0); ctx.restore();

        // Trajectories
        const colors = ['#dc2626', '#ea580c', '#ca8a04', '#16a34a', '#0891b2', '#7c3aed', '#db2777', '#4b5563'];
        trajectories.forEach((traj, idx) => {
            if (traj.length < 2) return;
            ctx.strokeStyle = colors[idx % colors.length];
            ctx.lineWidth = 1.8; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.setLineDash([]);
            ctx.beginPath(); ctx.moveTo(traj[0].x, traj[0].y + offY);
            for (let i = 1; i < traj.length; i++) ctx.lineTo(traj[i].x, traj[i].y + offY);
            ctx.stroke();
        });

        if (showInitialPoint && userPoints.length > 0) {
            userPoints.forEach((point, idx) => {
                const sx = gxOff + (point.x - tMin) * xScale;
                const sy = offY + canvas.height - gyOff - (point.y - yMin) * yScale;
                ctx.fillStyle = colors[idx % colors.length]; ctx.strokeStyle = '#000'; ctx.lineWidth = 1.5;
                ctx.beginPath(); ctx.arc(sx, sy, 4, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
            });
        }

        const link = document.createElement('a');
        link.download = 'phase-portrait-optimized.png';
        link.href = tmp.toDataURL('image/png');
        link.click();
    }
}

/* ================================================================
   BifurcationAnimator
   ================================================================ */
class BifurcationAnimator {
    constructor(app) {
        this.app = app;
        this.running = false;
        this.frameIndex = 0;
        this.frames = [];
    }

    async start() {
        if (this.running) { this.running = false; await new Promise(r => setTimeout(r, 100)); }

        this.frames = [];
        for (let mu = -2; mu <= 2; mu += 0.5) this.frames.push(mu);
        this.frameIndex = 0;

        await this._initStrategicTrajectories();
        this.running = true;
        this._loop();
    }

    stop() {
        this.running = false;
    }

    async _initStrategicTrajectories() {
        this.app.userPoints = [];
        this.app.trajectories = [];

        const pts = [
            { x: 0, y: 2 }, { x: 2, y: 0 }, { x: 0, y: -2 }, { x: -2, y: 0 },
            { x: 1.5, y: 1.5 }, { x: -1.5, y: 1.5 }, { x: 1.5, y: -1.5 }, { x: -1.5, y: -1.5 }
        ];
        this.app.userPoints = pts.map(p => ({ x: p.x, y: p.y }));

        const m = this.app.matrixInput.read();
        for (const p of pts) {
            const traj = await TrajectoryComputer.compute(p.x, p.y, m.a, m.b, m.c, m.d);
            this.app.trajectories.push(traj);
        }
        this.app.redraw();
    }

    async _loop() {
        if (!this.running) return;

        const mu = this.frames[this.frameIndex];
        this.frameIndex = (this.frameIndex + 1) % this.frames.length;

        const matrix = { a: 0, b: 1, c: -mu, d: 4 - mu * mu };
        this.app.matrixInput.setComputed(matrix);

        // Recompute trajectories from fixed initial points with new system
        this.app.trajectories = [];
        for (const p of this.app.userPoints) {
            const traj = await TrajectoryComputer.compute(p.x, p.y, matrix.a, matrix.b, matrix.c, matrix.d);
            this.app.trajectories.push(traj);
        }
        this.app.redraw();

        if (this.running) setTimeout(() => this._loop(), 1000);
    }
}

/* ================================================================
   PhasePortraitApp – top-level controller
   ================================================================ */
class PhasePortraitApp {
    constructor() {
        this.userPoints = [];
        this.trajectories = [];
        this.matrixInput = null;
        this.portrait = null;
        this.animator = null;
    }

    init() {
        this.matrixInput = new MatrixInput();
        this.portrait = new PhasePortraitCanvas(document.getElementById('canvas'));
        this.animator = new BifurcationAnimator(this);

        this._renderStaticKatex();
        this._bindExamples();
        this._bindCanvasClick();
        this._bindInputs();
        this.redraw();
    }

    /* ---- Drawing ---- */
    redraw() {
        const m = this.matrixInput.read();
        const cls = EquilibriumClassifier.classify(m.a, m.b, m.c, m.d);
        this._renderEquation(m);

        this.portrait.draw({
            matrix: m,
            arrowCount: parseInt(document.getElementById('arrow-count').value) || 30,
            arrowScale: parseFloat(document.getElementById('arrow-scale').value) || 1.2,
            arrowOpacity: parseFloat(document.getElementById('arrow-opacity').value) || 0.3,
            fieldColor: document.getElementById('field-color').value || '#000000',
            showGrid: document.getElementById('showGrid').checked,
            showInitialPoint: document.getElementById('showInitialPoint').checked,
            trajectories: this.trajectories,
            userPoints: this.userPoints,
            classificationInfo: cls
        });
    }

    /* ---- KaTeX equation rendering ---- */
    _renderStaticKatex() {
        katex.render(
            '\\begin{cases}\n \\dot{x} = ax + by \\\\\n \\dot{y} = cx + dy\n \\end{cases}',
            document.getElementById('equation-display'),
            { throwOnError: false, displayMode: true }
        );
    }

    _renderEquation({ a, b, c, d }) {
        const container = document.getElementById('canvas-equation');
        container.innerHTML = '';
        const fmt = (v) => { if (v === 0) return '0'; if (v === 1) return ''; if (v === -1) return '-'; return (Math.round(v * 100) / 100).toString(); };
        const aS = fmt(a), bS = fmt(b), cS = fmt(c), dS = fmt(d);
        const bSign = b >= 0 ? '+' : '', dSign = d >= 0 ? '+' : '';
        const tex = `\\begin{cases} \\dot{x} = ${aS === '' ? '' : aS}${aS === '' && a === -1 ? '-' : ''}x ${bSign}${bS}y \\\\ \\dot{y} = ${cS === '' ? '' : cS}${cS === '' && c === -1 ? '-' : ''}x ${dSign}${dS}y \\end{cases}`;
        katex.render(tex, container, { throwOnError: false, displayMode: true, fontSize: 18 });
    }

    /* ---- Examples ---- */
    _bindExamples() {
        document.querySelectorAll('.example').forEach((el) => {
            el.addEventListener('click', async () => {
                if (el.dataset.type) {
                    document.getElementById('instruction').style.display = 'none';
                    await this.animator.start();
                } else {
                    this.animator.stop();
                    this.matrixInput.write({
                        a: el.dataset.a, b: el.dataset.b,
                        c: el.dataset.c, d: el.dataset.d
                    });
                    this.matrixInput.clearComputed();
                    await this._initStrategicTrajectories();
                    document.getElementById('instruction').style.display = 'none';
                }
            });

            katex.render(
                el.querySelector('.matrix-latex').textContent,
                el.querySelector('.matrix-latex'),
                { throwOnError: false, displayMode: true }
            );
        });
    }

    async _initStrategicTrajectories() {
        this.userPoints = [];
        this.trajectories = [];
        const pts = [
            { x: 0, y: 2 }, { x: 2, y: 0 }, { x: 0, y: -2 }, { x: -2, y: 0 },
            { x: 1.5, y: 1.5 }, { x: -1.5, y: 1.5 }, { x: 1.5, y: -1.5 }, { x: -1.5, y: -1.5 }
        ];
        this.userPoints = pts.map(p => ({ x: p.x, y: p.y }));
        const m = this.matrixInput.read();
        for (const p of pts) {
            const traj = await TrajectoryComputer.compute(p.x, p.y, m.a, m.b, m.c, m.d);
            this.trajectories.push(traj);
        }
        this.redraw();
    }

    /* ---- Canvas click ---- */
    _bindCanvasClick() {
        const canvas = document.getElementById('canvas');
        canvas.addEventListener('click', (e) => {
            this.animator.stop();
            const rect = canvas.getBoundingClientRect();
            const px = e.clientX - rect.left;
            const py = e.clientY - rect.top;
            const P = 70;
            if (px < P || px > canvas.width - P || py < P || py > canvas.height - P) return;

            const tMin = -5, tMax = 5, yMin = -5, yMax = 5;
            const dW = canvas.width - 2 * P;
            const sc = dW / (tMax - tMin);
            const t = tMin + (px - P) / sc;
            const yVal = yMin + (canvas.height - P - py) / sc;

            this.userPoints.push({ x: t, y: yVal });
            const m = this.matrixInput.read();
            TrajectoryComputer.compute(t, yVal, m.a, m.b, m.c, m.d).then((traj) => {
                this.trajectories.push(traj);
                this.redraw();
            });
            document.getElementById('instruction').style.display = 'none';
        });
    }

    /* ---- Input listeners ---- */
    _bindInputs() {
        const debouncedRedraw = debounce(() => {
            this.userPoints = [];
            this.trajectories = [];
            this.redraw();
        }, 300);

        ['a', 'b', 'c', 'd'].forEach((id) => {
            document.getElementById(id).addEventListener('input', (e) => {
                this.animator.stop();
                e.target.removeAttribute('data-computed');
                this.userPoints = [];
                this.trajectories = [];
                debouncedRedraw();
            });
        });

        document.getElementById('field-color').addEventListener('change', () => this.redraw());

        const throttledRedraw = throttle(() => this.redraw(), 100);
        document.getElementById('arrow-count').addEventListener('input', throttledRedraw);
        document.getElementById('arrow-scale').addEventListener('input', throttledRedraw);
        document.getElementById('arrow-opacity').addEventListener('input', throttledRedraw);

        document.getElementById('showInitialPoint').addEventListener('change', () => this.redraw());
        document.getElementById('showGrid').addEventListener('change', () => this.redraw());
    }

    /* ---- Public actions (called from HTML onclick) ---- */
    clearAndDraw() {
        this.animator.stop();
        this.userPoints = [];
        this.trajectories = [];
        document.getElementById('instruction').style.display = 'block';
        this.redraw();
    }

    clearTrajectories() {
        this.animator.stop();
        this.userPoints = [];
        this.trajectories = [];
        this.redraw();
        document.getElementById('instruction').style.display = 'block';
    }

    downloadImage() {
        const m = this.matrixInput.read();
        const cls = EquilibriumClassifier.classify(m.a, m.b, m.c, m.d);
        ImageExporter.download(document.getElementById('canvas'), {
            matrix: m,
            classification: cls,
            trajectories: this.trajectories,
            userPoints: this.userPoints,
            arrowCount: parseInt(document.getElementById('arrow-count').value) || 30,
            arrowScale: parseFloat(document.getElementById('arrow-scale').value) || 1.2,
            arrowOpacity: parseFloat(document.getElementById('arrow-opacity').value) || 0.3,
            fieldColor: document.getElementById('field-color').value || '#000000',
            showGrid: document.getElementById('showGrid').checked,
            showInitialPoint: document.getElementById('showInitialPoint').checked
        });
    }
}

/* ================================================================
   Bootstrap
   ================================================================ */
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new PhasePortraitApp();
    app.init();
});

/* Global callbacks referenced by onclick in the HTML */
function clearAndDrawPhasePortrait() { app.clearAndDraw(); }
function clearUserPoints() { app.clearTrajectories(); }
function downloadImage() { app.downloadImage(); }
