/**
 * Linear Programming: Method of Corners – OOP Refactor
 *
 * Classes:
 *   ConstraintParser  – parse "2x+3y" style expressions into {a, b} coefficients
 *   MathFormatter     – fraction conversion, LaTeX formatting
 *   FeasibleRegion    – line intersection, corner points, convex hull, boundedness checks
 *   PlotRenderer      – builds Plotly traces for constraint lines, shading, corners
 *   SweepAnimator     – iso-profit/cost line animation
 *   CornersApp        – top-level controller (DOM, events, examples)
 */

/* ================================================================
   ConstraintParser
   ================================================================ */
class ConstraintParser {
    static evaluateFraction(fractionStr) {
        const parts = fractionStr.split('/');
        if (parts.length === 2) {
            const num = parseFloat(parts[0]);
            const den = parseFloat(parts[1]);
            if (!isNaN(num) && !isNaN(den) && den !== 0) return num / den;
        }
        return parseFloat(fractionStr);
    }

    static parseCoefficient(coeffStr) {
        if (coeffStr === '' || coeffStr === '+') return 1;
        if (coeffStr === '-') return -1;
        if (coeffStr.includes('/')) {
            return this.evaluateFraction(coeffStr.replace(/[()]/g, ''));
        }
        return parseFloat(coeffStr);
    }

    static parseLHS(lhsString) {
        let str = lhsString.replace(/\s+/g, '').toLowerCase().replace(/\*/g, '');
        let a = 0, b = 0;

        if (str === '') return { a: 0, b: 0 };
        if (str === 'x') return { a: 1, b: 0 };
        if (str === 'y') return { a: 0, b: 1 };
        if (str === '-x') return { a: -1, b: 0 };
        if (str === '-y') return { a: 0, b: -1 };

        const xPatterns = [/(\([+-]?\d+\/\d+\))x/, /([+-]?\d*\.?\d*)x/];
        for (const pattern of xPatterns) {
            const m = str.match(pattern);
            if (m) { a = this.parseCoefficient(m[1]); str = str.replace(m[0], ''); break; }
        }

        const yPatterns = [/(\([+-]?\d+\/\d+\))y/, /([+-]?\d*\.?\d*)y/];
        for (const pattern of yPatterns) {
            const m = str.match(pattern);
            if (m) { b = this.parseCoefficient(m[1]); str = str.replace(m[0], ''); break; }
        }

        if (str !== '' && !isNaN(parseFloat(str))) b = parseFloat(str);
        if (isNaN(a)) a = 0;
        if (isNaN(b)) b = 0;
        return { a, b };
    }
}

/* ================================================================
   MathFormatter
   ================================================================ */
class MathFormatter {
    static COLORS = ['#E41A1C', '#377EB8', '#4DAF4A', '#984EA3', '#FF7F00', '#A65628', '#F781BF', '#999999'];

    static toFraction(decimal, tolerance = 1e-6) {
        if (Math.abs(decimal - Math.round(decimal)) < tolerance) {
            return { numerator: Math.round(decimal), denominator: 1 };
        }
        const sign = decimal < 0 ? -1 : 1;
        decimal = Math.abs(decimal);
        let bestNumerator = Math.round(decimal), bestDenominator = 1;
        let bestError = Math.abs(decimal - bestNumerator);

        for (let d = 2; d <= 10000; d++) {
            const n = Math.round(decimal * d);
            const err = Math.abs(decimal - n / d);
            if (err < bestError) { bestNumerator = n; bestDenominator = d; bestError = err; }
            if (err < tolerance) break;
        }

        const gcd = (a, b) => b === 0 ? a : gcd(b, a % b);
        const div = gcd(bestNumerator, bestDenominator);
        return { numerator: sign * (bestNumerator / div), denominator: bestDenominator / div };
    }

    static formatNumber(num) {
        if (Number.isInteger(num)) return num.toString();
        return Math.round(num * 100) / 100;
    }

    static formatNumberAsLatex(num, useLatex = true) {
        const displayMode = document.getElementById('display-mode')?.value || 'decimal';
        if (displayMode === 'fraction') {
            const frac = this.toFraction(num);
            if (frac.denominator === 1) return frac.numerator.toString();
            return useLatex ? `\\dfrac{${frac.numerator}}{${frac.denominator}}` : `${frac.numerator}/${frac.denominator}`;
        }
        if (Number.isInteger(num)) return num.toString();
        return (Math.round(num * 100) / 100).toString();
    }

    static formatCoefficient(coeff, isY) {
        if (Math.abs(coeff) < 0.0001) return '0';
        if (Math.abs(coeff - 1) < 0.0001) return isY ? 'y' : 'x';
        if (Math.abs(coeff + 1) < 0.0001) return isY ? '-y' : '-x';
        const formatted = Number.isInteger(coeff) ? coeff.toString() : coeff.toFixed(2);
        return formatted + (isY ? 'y' : 'x');
    }

    static getLatexRelation(relation) {
        switch (relation) {
            case '<': return '\\lt';
            case '>': return '\\gt';
            case '≤': return '\\le';
            case '≥': return '\\ge';
            default: return relation;
        }
    }

    static formatLHS(ineq) {
        const a = this.formatCoefficient(ineq.a, false);
        const b = this.formatCoefficient(ineq.b, true);
        if (a === '0' && b === '0') return '0';
        if (a === '0') return b;
        if (b === '0') return a;
        const bSign = ineq.b < 0 ? '-' : '+';
        const bAbs = this.formatCoefficient(Math.abs(ineq.b), true);
        return `${a} ${bSign} ${bAbs}`;
    }

    static formatRHSForLatex(rhsString, rhsValue) {
        if (rhsString.includes('/')) {
            const parts = rhsString.split('/');
            if (parts.length === 2) {
                const num = parts[0].trim(), den = parts[1].trim();
                if (!isNaN(parseFloat(num)) && !isNaN(parseFloat(den))) return `\\dfrac{${num}}{${den}}`;
            }
        }
        if (!Number.isInteger(rhsValue)) {
            const frac = this.toFraction(rhsValue);
            if (frac.denominator !== 1) return `\\dfrac{${frac.numerator}}{${frac.denominator}}`;
        }
        return this.formatNumber(rhsValue);
    }

    static generateLatex(ineq, index) {
        const a = this.formatCoefficient(ineq.a, false);
        const b = this.formatCoefficient(ineq.b, true);
        const relation = this.getLatexRelation(ineq.relation);
        const c = this.formatRHSForLatex(ineq.rhsString, ineq.c);
        let latex;
        if (a === '0' && b === '0') latex = `0 ${relation} ${c}`;
        else if (a === '0') latex = `${b} ${relation} ${c}`;
        else if (b === '0') latex = `${a} ${relation} ${c}`;
        else {
            const bSign = ineq.b < 0 ? '-' : '+';
            const bAbs = this.formatCoefficient(Math.abs(ineq.b), true);
            latex = `${a} ${bSign} ${bAbs} ${relation} ${c}`;
        }
        return `\\color{${this.COLORS[index % this.COLORS.length]}}{${latex}}`;
    }

    static hexToRgb(hex) {
        const bigint = parseInt(hex.slice(1), 16);
        return { r: (bigint >> 16) & 255, g: (bigint >> 8) & 255, b: bigint & 255 };
    }
}

/* ================================================================
   FeasibleRegion – geometry computations
   ================================================================ */
class FeasibleRegion {
    static intersectLines(ineq1, ineq2) {
        const det = ineq1.a * ineq2.b - ineq2.a * ineq1.b;
        if (Math.abs(det) < 1e-8) return null;
        return [
            (ineq1.c * ineq2.b - ineq2.c * ineq1.b) / det,
            (ineq1.a * ineq2.c - ineq2.a * ineq1.c) / det
        ];
    }

    static pointSatisfiesAll(point, inequalities) {
        const [x, y] = point;
        for (const ineq of inequalities) {
            const val = ineq.a * x + ineq.b * y;
            const tol = 1e-6;
            if ((ineq.relation === '≤' || ineq.relation === '<') && val > ineq.c + tol) return false;
            if ((ineq.relation === '≥' || ineq.relation === '>') && val < ineq.c - tol) return false;
        }
        return true;
    }

    static findCornerPoints(inequalities) {
        if (inequalities.length < 2) return [];
        const points = [];
        for (let i = 0; i < inequalities.length; i++) {
            for (let j = i + 1; j < inequalities.length; j++) {
                const p = this.intersectLines(inequalities[i], inequalities[j]);
                if (p && this.pointSatisfiesAll(p, inequalities)) points.push(p);
            }
        }
        return points.filter((p, idx) =>
            points.findIndex(q => Math.abs(q[0] - p[0]) < 1e-6 && Math.abs(q[1] - p[1]) < 1e-6) === idx
        );
    }

    static sortPointsClockwise(points) {
        if (points.length < 3) return points;
        const cx = points.reduce((s, p) => s + p[0], 0) / points.length;
        const cy = points.reduce((s, p) => s + p[1], 0) / points.length;
        return points.sort((a, b) => Math.atan2(a[1] - cy, a[0] - cx) - Math.atan2(b[1] - cy, b[0] - cx));
    }

    static evaluateObjective(point, obj) {
        return obj.px * point[0] + obj.py * point[1];
    }

    static calculateBounds(inequalities) {
        if (inequalities.length === 0) return { xMin: -5, xMax: 5, yMin: -5, yMax: 5 };

        let xMin = -10, xMax = 10, yMin = -10, yMax = 10;
        inequalities.forEach(ineq => {
            if (Math.abs(ineq.a) > 0.001) { const xi = ineq.c / ineq.a; xMin = Math.min(xMin, xi); xMax = Math.max(xMax, xi); }
            if (Math.abs(ineq.b) > 0.001) { const yi = ineq.c / ineq.b; yMin = Math.min(yMin, yi); yMax = Math.max(yMax, yi); }
        });

        const cornerPoints = this.findCornerPoints(inequalities);
        const isBounded = cornerPoints.length > 0;
        let paddingFactor, minPadding;

        if (isBounded) {
            xMin = Math.min(...cornerPoints.map(p => p[0]));
            xMax = Math.max(...cornerPoints.map(p => p[0]));
            yMin = Math.min(...cornerPoints.map(p => p[1]));
            yMax = Math.max(...cornerPoints.map(p => p[1]));
            paddingFactor = 0.2; minPadding = 1;
        } else {
            paddingFactor = 0.4; minPadding = 4;
        }

        const rangeX = xMax - xMin || 10;
        const rangeY = yMax - yMin || 10;
        const padding = Math.max(rangeX * paddingFactor, rangeY * paddingFactor, minPadding);
        return { xMin: xMin - padding, xMax: xMax + padding, yMin: yMin - padding, yMax: yMax + padding };
    }

    static _checkBounds(inequalities) {
        let hasUpperX = false, hasLowerX = false, hasUpperY = false, hasLowerY = false;
        inequalities.forEach(ineq => {
            if (Math.abs(ineq.a - 1) < 0.001 && Math.abs(ineq.b) < 0.001 && (ineq.relation === '≤' || ineq.relation === '<')) hasUpperX = true;
            if (Math.abs(ineq.a - 1) < 0.001 && Math.abs(ineq.b) < 0.001 && (ineq.relation === '≥' || ineq.relation === '>')) hasLowerX = true;
            if (Math.abs(ineq.b - 1) < 0.001 && Math.abs(ineq.a) < 0.001 && (ineq.relation === '≤' || ineq.relation === '<')) hasUpperY = true;
            if (Math.abs(ineq.b - 1) < 0.001 && Math.abs(ineq.a) < 0.001 && (ineq.relation === '≥' || ineq.relation === '>')) hasLowerY = true;
            if (ineq.a > 0 && ineq.b > 0 && (ineq.relation === '≤' || ineq.relation === '<')) { hasUpperX = true; hasUpperY = true; }
            if (ineq.a < 0 && ineq.b < 0 && (ineq.relation === '≥' || ineq.relation === '>')) { hasUpperX = true; hasUpperY = true; }
            if (ineq.a > 0 && ineq.b > 0 && (ineq.relation === '≥' || ineq.relation === '>')) { hasLowerX = true; hasLowerY = true; }
            if (ineq.a < 0 && ineq.b < 0 && (ineq.relation === '≤' || ineq.relation === '<')) { hasLowerX = true; hasLowerY = true; }
        });
        return { hasUpperX, hasLowerX, hasUpperY, hasLowerY };
    }

    static isRegionUnbounded(inequalities) {
        const { hasUpperX, hasLowerX, hasUpperY, hasLowerY } = this._checkBounds(inequalities);
        return !(hasUpperX && hasLowerX && hasUpperY && hasLowerY);
    }

    static hasMaximum(inequalities, objective) {
        if (!this.isRegionUnbounded(inequalities)) return true;
        const { hasUpperX, hasLowerX, hasUpperY, hasLowerY } = this._checkBounds(inequalities);
        if (!hasUpperX && objective.px > 0.001) return false;
        if (!hasLowerX && objective.px < -0.001) return false;
        if (!hasUpperY && objective.py > 0.001) return false;
        if (!hasLowerY && objective.py < -0.001) return false;
        return true;
    }

    static hasMinimum(inequalities, objective) {
        if (!this.isRegionUnbounded(inequalities)) return true;
        const { hasUpperX, hasLowerX, hasUpperY, hasLowerY } = this._checkBounds(inequalities);
        if (!hasLowerX && objective.px > 0.001) return false;
        if (!hasUpperX && objective.px < -0.001) return false;
        if (!hasLowerY && objective.py > 0.001) return false;
        if (!hasUpperY && objective.py < -0.001) return false;
        return true;
    }
}

/* ================================================================
   PlotRenderer – builds Plotly traces and renders
   ================================================================ */
class PlotRenderer {
    constructor(plotElId) {
        this.plotElId = plotElId;
        this.initialized = false;
    }

    static _plotlyLayout(bounds) {
        return {
            plot_bgcolor: 'white', paper_bgcolor: 'white',
            xaxis: {
                title: { text: 'x', font: { size: 20 } },
                range: [bounds.xMin, bounds.xMax],
                showgrid: true, gridcolor: 'rgba(220,220,220,0.6)', gridwidth: 1,
                zeroline: true, zerolinecolor: '#333', zerolinewidth: 2,
                showline: true, linecolor: '#333', linewidth: 2, tickfont: { size: 16 }
            },
            yaxis: {
                title: { text: 'y', font: { size: 20 } },
                range: [bounds.yMin, bounds.yMax],
                showgrid: true, gridcolor: 'rgba(220,220,220,0.6)', gridwidth: 1,
                zeroline: true, zerolinecolor: '#333', zerolinewidth: 2,
                showline: true, linecolor: '#333', linewidth: 2,
                scaleanchor: 'x', scaleratio: 1, tickfont: { size: 16 }
            },
            margin: { l: 60, r: 30, t: 30, b: 60 },
            hovermode: false, dragmode: 'pan', showlegend: false
        };
    }

    static _plotlyConfig() {
        return { responsive: true, displayModeBar: true, displaylogo: false, modeBarButtonsToRemove: ['lasso2d', 'select2d'] };
    }

    static extendLineToEdges(ineq, bounds) {
        const ext = 0.5 * (bounds.xMax - bounds.xMin);
        const x1 = bounds.xMin - ext, x2 = bounds.xMax + ext;
        if (Math.abs(ineq.b) <= 0.001) return null;
        return { x: [x1, x2], y: [(ineq.c - ineq.a * x1) / ineq.b, (ineq.c - ineq.a * x2) / ineq.b] };
    }

    static buildConstraintTraces(inequalities, bounds, isReverse) {
        const data = [];
        const fmt = MathFormatter;

        inequalities.forEach((ineq, i) => {
            const isStrict = ineq.relation === '<' || ineq.relation === '>';
            const dash = isStrict ? 'dash' : 'solid';
            const rgb = fmt.hexToRgb(ineq.color);
            const shadeColor = `rgba(${rgb.r},${rgb.g},${rgb.b},0.15)`;

            // Constraint line
            if (Math.abs(ineq.b) > 0.001) {
                const ext = this.extendLineToEdges(ineq, bounds);
                if (ext) data.push({ x: ext.x, y: ext.y, mode: 'lines', line: { color: ineq.color, width: 3, dash }, showlegend: false, hoverinfo: 'none' });
            } else if (Math.abs(ineq.a) > 0.001) {
                const xVal = ineq.c / ineq.a;
                data.push({ x: [xVal, xVal], y: [bounds.yMin - 10, bounds.yMax + 10], mode: 'lines', line: { color: ineq.color, width: 3, dash }, showlegend: false, hoverinfo: 'none' });
            }

            // Shading polygon
            let x = [], y = [];
            if (Math.abs(ineq.b) > 0.001) {
                let shadeAbove = ((ineq.relation === '≥' || ineq.relation === '>') && ineq.b > 0) ||
                    ((ineq.relation === '≤' || ineq.relation === '<') && ineq.b < 0);
                if (isReverse) shadeAbove = !shadeAbove;
                const yL = (ineq.c - ineq.a * bounds.xMin) / ineq.b;
                const yR = (ineq.c - ineq.a * bounds.xMax) / ineq.b;
                x = [bounds.xMin, bounds.xMax, bounds.xMax, bounds.xMin];
                y = shadeAbove ? [yL, yR, bounds.yMax, bounds.yMax] : [yL, yR, bounds.yMin, bounds.yMin];
            } else if (Math.abs(ineq.a) > 0.001) {
                const xVal = ineq.c / ineq.a;
                let shadeRight = ((ineq.relation === '≥' || ineq.relation === '>') && ineq.a > 0) ||
                    ((ineq.relation === '≤' || ineq.relation === '<') && ineq.a < 0);
                if (isReverse) shadeRight = !shadeRight;
                if (shadeRight) { x = [xVal, bounds.xMax, bounds.xMax, xVal]; y = [bounds.yMin, bounds.yMin, bounds.yMax, bounds.yMax]; }
                else { x = [bounds.xMin, xVal, xVal, bounds.xMin]; y = [bounds.yMin, bounds.yMin, bounds.yMax, bounds.yMax]; }
            } else return;

            data.push({ x, y, fill: 'toself', fillcolor: shadeColor, line: { width: 0 }, mode: 'lines', showlegend: false, hoverinfo: 'none' });
        });

        return data;
    }

    static buildCornerTraces(cornerPoints, cornerLabels, optimalIndices = null, atOptimal = false) {
        const data = [];
        cornerPoints.forEach((point, i) => {
            const label = cornerLabels[i] || String.fromCharCode(65 + i);
            const isOpt = optimalIndices && optimalIndices.includes(i) && atOptimal;
            data.push({
                x: [point[0]], y: [point[1]],
                mode: 'markers+text',
                marker: { size: isOpt ? 20 : 14, color: isOpt ? '#27ae60' : '#2c3e50', line: { color: 'white', width: 3 } },
                text: [label], textposition: 'top center',
                textfont: { size: isOpt ? 22 : 18, family: 'Arial', weight: 'bold', color: isOpt ? '#27ae60' : '#2c3e50' },
                showlegend: false, hoverinfo: 'none'
            });
        });
        return data;
    }

    static buildObjectiveLineTrace(pValue, objective, bounds, atOptimal) {
        const lineColor = atOptimal ? '#27ae60' : '#e74c3c';
        const lineWidth = atOptimal ? 5 : 4;
        if (Math.abs(objective.py) > 0.001) {
            const ext = 0.5 * (bounds.xMax - bounds.xMin);
            const x1 = bounds.xMin - ext, x2 = bounds.xMax + ext;
            return { x: [x1, x2], y: [(pValue - objective.px * x1) / objective.py, (pValue - objective.px * x2) / objective.py],
                mode: 'lines', line: { color: lineColor, width: lineWidth, dash: 'dashdot' }, showlegend: false, hoverinfo: 'none' };
        }
        if (Math.abs(objective.px) > 0.001) {
            const xVal = pValue / objective.px;
            return { x: [xVal, xVal], y: [bounds.yMin - 10, bounds.yMax + 10],
                mode: 'lines', line: { color: lineColor, width: lineWidth, dash: 'dashdot' }, showlegend: false, hoverinfo: 'none' };
        }
        return null;
    }

    static buildOptimalEdgeTraces(cornerPoints, optimalIndices) {
        const data = [];
        const sorted = [...optimalIndices].sort((a, b) => a - b);
        for (let i = 0; i < sorted.length - 1; i++) {
            const i1 = sorted[i], i2 = sorted[i + 1];
            if (i2 - i1 === 1 || (i1 === 0 && i2 === cornerPoints.length - 1)) {
                data.push({ x: [cornerPoints[i1][0], cornerPoints[i2][0]], y: [cornerPoints[i1][1], cornerPoints[i2][1]],
                    mode: 'lines', line: { color: '#27ae60', width: 6 }, showlegend: false, hoverinfo: 'none' });
            }
        }
        if (sorted.includes(0) && sorted.includes(cornerPoints.length - 1)) {
            const p1 = cornerPoints[0], p2 = cornerPoints[cornerPoints.length - 1];
            data.push({ x: [p1[0], p2[0]], y: [p1[1], p2[1]], mode: 'lines', line: { color: '#27ae60', width: 6 }, showlegend: false, hoverinfo: 'none' });
        }
        return data;
    }

    render(data, bounds) {
        const layout = PlotRenderer._plotlyLayout(bounds);
        const config = PlotRenderer._plotlyConfig();
        if (this.initialized) {
            Plotly.react(this.plotElId, data, layout, config);
        } else {
            Plotly.newPlot(this.plotElId, data, layout, config);
            this.initialized = true;
        }
    }
}

/* ================================================================
   SweepAnimator
   ================================================================ */
class SweepAnimator {
    constructor(app) {
        this.app = app;
    }

    async play() {
        const app = this.app;
        const inequalities = app.getInequalities();
        const objective = app.getObjective();
        const bounds = FeasibleRegion.calculateBounds(inequalities);
        const rawCorners = FeasibleRegion.findCornerPoints(inequalities);
        const cornerPoints = FeasibleRegion.sortPointsClockwise(rawCorners);

        if (cornerPoints.length === 0) { alert('No corner points found! Please ensure you have a bounded feasible region.'); return; }
        if (objective.px === 0 && objective.py === 0) { alert('Please enter a valid objective function (e.g., 3x+4y)'); return; }

        const optType = document.getElementById('optimization-type').value;
        let isMaximize = true;
        if (optType === 'auto') {
            const hasMax = FeasibleRegion.hasMaximum(inequalities, objective);
            const hasMin = FeasibleRegion.hasMinimum(inequalities, objective);
            if (!hasMax && !hasMin) { alert('Cannot determine optimization type. The region appears to be unbounded in both directions.'); return; }
            isMaximize = hasMax;
        } else {
            isMaximize = optType === 'maximize';
        }

        if (isMaximize && !FeasibleRegion.hasMaximum(inequalities, objective)) { alert('No maximum exists! The objective function is unbounded above for this feasible region.\n\nTry minimizing instead.'); return; }
        if (!isMaximize && !FeasibleRegion.hasMinimum(inequalities, objective)) { alert('No minimum exists! The objective function is unbounded below for this feasible region.\n\nTry maximizing instead.'); return; }

        const button = document.getElementById('play-sweep');
        button.disabled = true;
        button.textContent = '⏸ Animation Running...';

        const pValues = cornerPoints.map(p => FeasibleRegion.evaluateObjective(p, objective));
        const minP = Math.min(...pValues), maxP = Math.max(...pValues);
        const optimalP = isMaximize ? maxP : minP;
        const tol = 1e-6;
        const optimalIndices = pValues.map((v, i) => Math.abs(v - optimalP) < tol ? i : -1).filter(i => i >= 0);

        const range = maxP - minP;
        const startP = isMaximize ? (minP - range * 0.3) : (maxP + range * 0.3);
        const endP = isMaximize ? (maxP + range * 0.1) : (minP - range * 0.1);

        const display = document.getElementById('p-value-display');
        display.classList.add('active');
        display.classList.remove('maximum');

        const duration = parseInt(document.getElementById('animation-speed').value) || 3000;
        const fps = 30;
        const frames = Math.floor(duration / 1000 * fps);
        let currentFrame = 0;
        const isReverse = app.getShadingMode() === 'reverse';

        const animate = () => {
            if (currentFrame >= frames) {
                this._onComplete(display, button, isMaximize, optimalP, optimalIndices, cornerPoints, app);
                return;
            }

            const t = currentFrame / frames;
            const easeT = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
            const currentP = startP + (endP - startP) * easeT;

            document.getElementById('p-value-text').textContent = `P = ${MathFormatter.formatNumberAsLatex(currentP, false)}`;
            const atOptimal = isMaximize ? (currentP >= optimalP - range * 0.05) : (currentP <= optimalP + range * 0.05);
            display.style.borderColor = atOptimal ? '#f39c12' : '#3498db';
            display.style.background = atOptimal ? 'rgba(243,156,18,0.95)' : 'rgba(255,255,255,0.95)';
            display.style.color = atOptimal ? 'white' : '#2c3e50';

            const reachedOptimal = isMaximize ? (currentP >= optimalP) : (currentP <= optimalP);
            const data = [
                ...PlotRenderer.buildConstraintTraces(inequalities, bounds, isReverse),
            ];
            const objTrace = PlotRenderer.buildObjectiveLineTrace(currentP, objective, bounds, reachedOptimal);
            if (objTrace) data.push(objTrace);
            if (reachedOptimal && optimalIndices.length > 1) data.push(...PlotRenderer.buildOptimalEdgeTraces(cornerPoints, optimalIndices));
            data.push(...PlotRenderer.buildCornerTraces(cornerPoints, app.cornerLabels, optimalIndices, reachedOptimal));

            app.plotRenderer.render(data, bounds);
            currentFrame++;
            requestAnimationFrame(animate);
        };

        animate();
    }

    _onComplete(display, button, isMaximize, optimalP, optimalIndices, cornerPoints, app) {
        display.classList.add('maximum');
        const optLabel = isMaximize ? 'Maximum' : 'Minimum';
        let message;

        if (optimalIndices.length === 1) {
            const lbl = app.cornerLabels[optimalIndices[0]];
            const pt = cornerPoints[optimalIndices[0]];
            const xC = MathFormatter.formatNumberAsLatex(pt[0], false);
            const yC = MathFormatter.formatNumberAsLatex(pt[1], false);
            message = `<strong>${optLabel}: P = ${MathFormatter.formatNumberAsLatex(optimalP, false)}</strong><br>`;
            message += `<strong>at point ${lbl} (${xC}, ${yC})</strong><br>`;
            message += `<span style="color:rgba(255,255,255,0.8);font-size:16px;margin-top:8px;display:inline-block;">Click to close</span>`;
        } else {
            const coordsList = optimalIndices.map(i => {
                const pt = cornerPoints[i];
                return `${app.cornerLabels[i]}(${MathFormatter.formatNumberAsLatex(pt[0], false)}, ${MathFormatter.formatNumberAsLatex(pt[1], false)})`;
            }).join(', ');
            message = `<strong>${optLabel}: P = ${MathFormatter.formatNumberAsLatex(optimalP, false)}</strong><br>`;
            message += `<strong>Along edge: ${coordsList}</strong><br>`;
            message += `<span style="color:rgba(255,255,255,0.8);font-size:16px;margin-top:8px;display:inline-block;">Click to close</span>`;
        }

        document.getElementById('p-value-text').innerHTML = message;
        button.disabled = false;
        button.textContent = '▶ Play Sweep Animation';

        const closeHandler = () => {
            display.classList.remove('active', 'maximum');
            app.updatePlot();
            display.removeEventListener('click', closeHandler);
        };
        display.addEventListener('click', closeHandler);
    }
}

/* ================================================================
   CornersApp – top-level controller
   ================================================================ */
class CornersApp {
    constructor() {
        this.cornerLabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];
        this.plotRenderer = new PlotRenderer('plot');
        this.sweepAnimator = new SweepAnimator(this);
    }

    init() {
        this._renderKatex();
        this._bindEvents();
        setTimeout(() => {
            this.updatePlot();
            this.loadExample('feasible-region');
        }, 100);
    }

    /* ---- KaTeX setup ---- */
    _renderKatex() {
        document.getElementById('current-year').textContent = new Date().getFullYear();
        setTimeout(() => {
            const pageTitle = document.getElementById('page-title');
            if (pageTitle && typeof katex !== 'undefined') {
                try { katex.render('\\text{Linear Programming: Method of Corners}', pageTitle, { throwOnError: false }); } catch (e) { }
            }
        }, 200);
        setTimeout(() => {
            const el = document.getElementById('non-neg-latex');
            if (el && typeof katex !== 'undefined') katex.render('x, y \\ge 0', el, { throwOnError: false });
        }, 100);
    }

    /* ---- Events ---- */
    _bindEvents() {
        document.getElementById('add-inequality').addEventListener('click', () => this.addInequality());
        document.getElementById('add-non-negativity').addEventListener('click', () => this.addNonNegativity());
        document.getElementById('update-plot').addEventListener('click', () => this.updatePlot());
        document.getElementById('play-sweep').addEventListener('click', () => this.sweepAnimator.play());
        document.getElementById('clear-all').addEventListener('click', () => this.clearAll());
        document.getElementById('objective-function').addEventListener('input', () => this.updatePlot());

        setTimeout(() => {
            const dm = document.getElementById('display-mode');
            if (dm) dm.addEventListener('change', () => this.updatePlot());
        }, 200);

        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.loadExample(e.currentTarget.dataset.example));
        });

        document.querySelectorAll('input[name="shading-mode"]').forEach(radio => {
            radio.addEventListener('change', () => this.updatePlot());
        });

        window.addEventListener('resize', () => { if (this.plotRenderer.initialized) this.updatePlot(); });
    }

    /* ---- DOM helpers ---- */
    getShadingMode() {
        const sel = document.querySelector('input[name="shading-mode"]:checked');
        return sel ? sel.value : 'reverse';
    }

    createInequalityRow(data = { lhs: 'x', relation: '≥', rhs: 0 }) {
        const row = document.createElement('div');
        row.className = 'ineq-row';
        row.innerHTML = `
            <input type="text" class="lhs-input" placeholder="e.g., 2x+3y" value="${data.lhs}">
            <select class="relation-select">
                <option value="≤" ${data.relation === '≤' ? 'selected' : ''}>≤</option>
                <option value="≥" ${data.relation === '≥' ? 'selected' : ''}>≥</option>
                <option value="<" ${data.relation === '<' ? 'selected' : ''}>&lt;</option>
                <option value=">" ${data.relation === '>' ? 'selected' : ''}>&gt;</option>
            </select>
            <input type="text" class="rhs-input" placeholder="10 or 10/3" value="${data.rhs}">
            <button class="remove-btn" title="Remove">×</button>`;
        row.querySelector('.remove-btn').addEventListener('click', () => { row.remove(); this.updatePlot(); });
        row.querySelectorAll('input, select').forEach(el => {
            el.addEventListener('input', () => this.updatePlot());
            el.addEventListener('change', () => this.updatePlot());
        });
        return row;
    }

    addInequality(data) {
        document.getElementById('inequality-inputs').appendChild(this.createInequalityRow(data));
        this.updatePlot();
    }

    addNonNegativity() {
        let hasX = false, hasY = false;
        document.querySelectorAll('.ineq-row').forEach(row => {
            const lhs = row.querySelector('.lhs-input').value.trim().toLowerCase();
            if (lhs === 'x') hasX = true;
            if (lhs === 'y') hasY = true;
        });
        if (!hasX) this.addInequality({ lhs: 'x', relation: '≥', rhs: 0 });
        if (!hasY) this.addInequality({ lhs: 'y', relation: '≥', rhs: 0 });
        if (hasX && hasY) alert('Non-negativity constraints x ≥ 0 and y ≥ 0 are already present.');
    }

    getInequalities() {
        const ineqs = [];
        document.querySelectorAll('.ineq-row').forEach((row, i) => {
            const lhs = row.querySelector('.lhs-input').value || '';
            const relation = row.querySelector('.relation-select').value;
            const rhsString = row.querySelector('.rhs-input').value || '0';
            const rhs = ConstraintParser.evaluateFraction(rhsString);
            const coeffs = ConstraintParser.parseLHS(lhs);
            ineqs.push({ a: coeffs.a, b: coeffs.b, c: rhs, relation, color: MathFormatter.COLORS[i % MathFormatter.COLORS.length], lhsString: lhs, rhsString: rhsString.trim() });
        });
        return ineqs;
    }

    getObjective() {
        const expr = document.getElementById('objective-function').value.trim().toLowerCase() || '0';
        const coeffs = ConstraintParser.parseLHS(expr);
        return { px: coeffs.a, py: coeffs.b };
    }

    /* ---- Display ---- */
    _updateInequalitiesDisplay(inequalities) {
        const display = document.getElementById('inequalities-display');
        if (inequalities.length === 0) { display.innerHTML = '<span style="color:#adb5bd;">Add inequalities below</span>'; return; }
        display.innerHTML = '';
        inequalities.forEach((ineq, i) => {
            const container = document.createElement('div');
            container.className = 'inequality-item';
            const latexSpan = document.createElement('span');
            latexSpan.className = 'inequality-katex';
            container.appendChild(latexSpan);
            try { katex.render(MathFormatter.generateLatex(ineq, i), latexSpan, { throwOnError: false }); }
            catch { latexSpan.textContent = `${MathFormatter.formatLHS(ineq)} ${ineq.relation} ${ineq.c}`; }
            display.appendChild(container);
        });
    }

    _updateCornerPointsTable(cornerPoints, obj, inequalities) {
        const tbody = document.querySelector('#corner-points-table tbody');
        tbody.innerHTML = '';
        if (cornerPoints.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:#adb5bd;font-style:italic;">No corner points (unbounded or empty region)</td></tr>';
            return;
        }

        const pValues = cornerPoints.map(p => FeasibleRegion.evaluateObjective(p, obj));
        const minP = Math.min(...pValues), maxP = Math.max(...pValues);
        const tol = 1e-6;
        const minIdx = pValues.map((v, i) => Math.abs(v - minP) < tol ? i : -1).filter(i => i >= 0);
        const maxIdx = pValues.map((v, i) => Math.abs(v - maxP) < tol ? i : -1).filter(i => i >= 0);

        cornerPoints.forEach((p, i) => {
            const val = FeasibleRegion.evaluateObjective(p, obj);
            const label = this.cornerLabels[i] || String.fromCharCode(65 + i);
            const tr = document.createElement('tr');
            if (minIdx.includes(i) || maxIdx.includes(i)) { tr.style.backgroundColor = '#e8f5e9'; tr.style.fontWeight = '600'; }

            const labelCell = document.createElement('td'); labelCell.className = 'corner-label'; labelCell.textContent = label;
            const coordCell = document.createElement('td'); coordCell.className = 'corner-coordinates';
            try { katex.render(`\\left(${MathFormatter.formatNumberAsLatex(p[0], true)}, ${MathFormatter.formatNumberAsLatex(p[1], true)}\\right)`, coordCell, { throwOnError: false }); }
            catch { coordCell.textContent = `(${MathFormatter.formatNumber(p[0])}, ${MathFormatter.formatNumber(p[1])})`; }
            const valueCell = document.createElement('td'); valueCell.className = 'objective-value';
            try { katex.render(MathFormatter.formatNumberAsLatex(val, true), valueCell, { throwOnError: false }); }
            catch { valueCell.textContent = MathFormatter.formatNumber(val); }

            tr.appendChild(labelCell); tr.appendChild(coordCell); tr.appendChild(valueCell);
            tbody.appendChild(tr);
        });

        const hasMax = FeasibleRegion.hasMaximum(inequalities, obj);
        const hasMin = FeasibleRegion.hasMinimum(inequalities, obj);
        if (minIdx.length > 1 || maxIdx.length > 1 || !hasMax || !hasMin) {
            const tr = document.createElement('tr'); tr.style.borderTop = '2px solid #2c3e50'; tr.style.fontStyle = 'italic';
            const td = document.createElement('td'); td.colSpan = 3; td.style.padding = '12px'; td.style.textAlign = 'center';
            let msg = '';
            if (maxIdx.length > 1) msg += `<span style="color:#27ae60;font-weight:600;">Maximum occurs along edge: ${maxIdx.map(i => this.cornerLabels[i]).join(', ')}</span>`;
            if (minIdx.length > 1) { if (msg) msg += '<br>'; msg += `<span style="color:#27ae60;font-weight:600;">Minimum occurs along edge: ${minIdx.map(i => this.cornerLabels[i]).join(', ')}</span>`; }
            if (!hasMax) { if (msg) msg += '<br>'; msg += '<span style="color:#e74c3c;font-weight:600;">⚠ No maximum (unbounded above)</span>'; }
            if (!hasMin) { if (msg) msg += '<br>'; msg += '<span style="color:#e74c3c;font-weight:600;">⚠ No minimum (unbounded below)</span>'; }
            td.innerHTML = msg; tr.appendChild(td); tbody.appendChild(tr);
        }
    }

    /* ---- Main update ---- */
    updatePlot() {
        const inequalities = this.getInequalities();
        const objective = this.getObjective();
        this._updateInequalitiesDisplay(inequalities);
        const bounds = FeasibleRegion.calculateBounds(inequalities);
        const cornerPoints = FeasibleRegion.sortPointsClockwise(FeasibleRegion.findCornerPoints(inequalities));
        this._updateCornerPointsTable(cornerPoints, objective, inequalities);

        const isReverse = this.getShadingMode() === 'reverse';
        const data = [
            ...PlotRenderer.buildConstraintTraces(inequalities, bounds, isReverse),
            ...PlotRenderer.buildCornerTraces(cornerPoints, this.cornerLabels)
        ];
        this.plotRenderer.render(data, bounds);
    }

    /* ---- Clear / Examples ---- */
    clearAll() {
        if (confirm('Clear all inequalities?')) {
            document.getElementById('inequality-inputs').innerHTML = '';
            document.getElementById('objective-function').value = '';
            this.updatePlot();
        }
    }

    loadExample(name) {
        const examples = {
            'feasible-region': [
                { lhs: 'x', relation: '≥', rhs: 0 }, { lhs: 'y', relation: '≥', rhs: 0 },
                { lhs: '2x+y', relation: '≤', rhs: 10 }, { lhs: 'x+2y', relation: '≤', rhs: 8 }
            ],
            'unbounded': [
                { lhs: 'x', relation: '≥', rhs: 0 }, { lhs: 'y', relation: '≥', rhs: 0 },
                { lhs: '2x+y', relation: '≥', rhs: 10 }, { lhs: 'x+2y', relation: '≥', rhs: 8 }
            ],
            'single-halfplane': [{ lhs: 'x+y', relation: '≥', rhs: 3 }]
        };
        const example = examples[name];
        if (!example) return;

        document.getElementById('inequality-inputs').innerHTML = '';
        example.forEach(d => this.addInequality(d));
        if (name === 'feasible-region') document.getElementById('objective-function').value = '3x+4y';
        else if (name === 'unbounded') document.getElementById('objective-function').value = 'x+y';
        else document.getElementById('objective-function').value = '';
        this.updatePlot();
    }
}

/* ================================================================
   Bootstrap
   ================================================================ */
document.addEventListener('DOMContentLoaded', () => {
    const app = new CornersApp();
    app.init();
});
