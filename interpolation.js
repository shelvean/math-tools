/**
 * Polynomial Interpolation – OOP Refactor
 *
 * Classes:
 *   MathFormatter   – LaTeX / fraction formatting utilities
 *   LinearSolver    – Gaussian elimination
 *   MonomialMethod, LagrangeMethod, NewtonMethod,
 *   HermiteMethod, NaturalCubicSplineMethod, ClampedCubicSplineMethod
 *                   – Strategy classes for each interpolation method
 *   InterpolationPlotter – D3-based SVG chart + PNG export
 *   InterpolationApp     – top-level controller (DOM, state, events)
 */

/* ================================================================
   MathFormatter
   ================================================================ */
class MathFormatter {
    static gcd(a, b) {
        a = Math.abs(a);
        b = Math.abs(b);
        while (b !== 0) {
            const t = b;
            b = a % b;
            a = t;
        }
        return a;
    }

    static toFraction(num, tolerance = 1e-10, maxIterations = 100) {
        if (isNaN(num)) return '\\text{NaN}';
        if (!isFinite(num)) return num > 0 ? '\\infty' : '-\\infty';
        if (Math.abs(num) < 1e-13) return '0';

        // Detect multiples of pi
        const piMultiples = [
            { value: Math.PI, tex: '\\pi' },
            { value: Math.PI / 2, tex: '\\frac{\\pi}{2}' },
            { value: Math.PI / 3, tex: '\\frac{\\pi}{3}' },
            { value: Math.PI / 4, tex: '\\frac{\\pi}{4}' },
            { value: Math.PI / 6, tex: '\\frac{\\pi}{6}' },
            { value: 2 * Math.PI / 3, tex: '\\frac{2\\pi}{3}' },
            { value: 3 * Math.PI / 4, tex: '\\frac{3\\pi}{4}' },
            { value: 5 * Math.PI / 6, tex: '\\frac{5\\pi}{6}' },
            { value: 2 * Math.PI, tex: '2\\pi' },
        ];
        for (const { value, tex } of piMultiples) {
            if (Math.abs(num - value) < tolerance) return tex;
            if (Math.abs(num + value) < tolerance) return `-${tex}`;
        }

        // Other transcendental values
        if (Math.abs(num - Math.sqrt(3) / 2) < tolerance) return '\\frac{\\sqrt{3}}{2}';
        if (Math.abs(num - Math.exp(2)) < tolerance) return 'e^{2}';

        // Small numbers → scientific notation
        if (Math.abs(num) < 1e-3 && Math.abs(num) >= 1e-13) {
            const sign = num < 0 ? '-' : '';
            const absNum = Math.abs(num);
            const exponent = Math.floor(Math.log10(absNum));
            const coefficient = absNum / Math.pow(10, exponent);
            const coeffRounded = Math.round(coefficient * 100) / 100;
            return `${sign}${coeffRounded} \\cdot 10^{${exponent}}`;
        }

        // Continued-fraction conversion
        const sign = num < 0 ? '-' : '';
        num = Math.abs(num);
        let h1 = 1, h2 = 0, k1 = 0, k2 = 1, b = num;
        for (let i = 0; i < maxIterations; i++) {
            const a = Math.floor(b);
            const h = a * h1 + h2;
            const k = a * k1 + k2;
            if (Math.abs(num - h / k) < tolerance) {
                const g = MathFormatter.gcd(h, k);
                const numFinal = h / g;
                const denFinal = k / g;
                if (denFinal > 100) {
                    return sign + parseFloat(num).toFixed(4).replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1');
                }
                if (denFinal === 1) return sign + numFinal;
                return sign + '\\dfrac{' + numFinal + '}{' + denFinal + '}';
            }
            h2 = h1; h1 = h;
            k2 = k1; k1 = k;
            b = 1 / (b - a);
        }
        return sign + parseFloat(num).toFixed(4).replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1');
    }

    static formatNumber(num) {
        return MathFormatter.toFraction(num);
    }

    static formatTerm(xVal) {
        if (xVal === 0) return 'x';
        const valStr = MathFormatter.formatNumber(xVal);
        return xVal > 0
            ? `\\left( x - ${valStr} \\right)`
            : `\\left( x + ${MathFormatter.formatNumber(-xVal)} \\right)`;
    }

    static groupFactors(factors) {
        const termCounts = new Map();
        factors.forEach(term => termCounts.set(term, (termCounts.get(term) || 0) + 1));

        const getXVal = (term) => {
            if (term === 'x') return 0;
            if (term.startsWith('\\left( x - ')) {
                const valStr = term.slice(11, -8);
                try { return parseFloat(valStr) || math.evaluate(valStr); } catch { return 0; }
            }
            if (term.startsWith('\\left( x + ')) {
                const valStr = term.slice(11, -8);
                try { return -parseFloat(valStr) || -math.evaluate(valStr); } catch { return 0; }
            }
            return 0;
        };

        const uniqueTerms = Array.from(termCounts.keys()).sort((a, b) => getXVal(a) - getXVal(b));
        return uniqueTerms.map(term => {
            const count = termCounts.get(term);
            return count > 1 ? term + '^{' + count + '}' : term;
        }).join('');
    }

    /** Clean up consecutive sign characters in a LaTeX polynomial string. */
    static cleanPolyTex(tex) {
        return tex.replace(/\+-/g, '-').replace(/[-]+/g, '-').replace(/--/g, '+');
    }
}

/* ================================================================
   LinearSolver
   ================================================================ */
class LinearSolver {
    /** Solve Ax = b via Gaussian elimination with partial pivoting. */
    static solve(A, b) {
        const n = A.length;
        const aug = A.map((row, i) => [...row, b[i]]);

        for (let p = 0; p < n; p++) {
            let max = p;
            for (let i = p + 1; i < n; i++) {
                if (Math.abs(aug[i][p]) > Math.abs(aug[max][p])) max = i;
            }
            [aug[p], aug[max]] = [aug[max], aug[p]];
            if (Math.abs(aug[p][p]) < 1e-12) throw new Error('Matrix is singular or near-singular');

            for (let i = p + 1; i < n; i++) {
                const alpha = aug[i][p] / aug[p][p];
                for (let j = p; j <= n; j++) aug[i][j] -= alpha * aug[p][j];
            }
        }

        const x = new Array(n).fill(0);
        for (let i = n - 1; i >= 0; i--) {
            let sum = 0;
            for (let j = i + 1; j < n; j++) sum += aug[i][j] * x[j];
            x[i] = (aug[i][n] - sum) / aug[i][i];
            if (!isFinite(x[i])) throw new Error('Non-finite solution detected');
        }
        return x;
    }
}

/* ================================================================
   Interpolation Method – Strategy Classes
   Each exposes:
     compute(x, y, options) → { pFunc, sections: { polynomial, table, matrix } }
   where each section is { el: HTMLElement, available: boolean }
   ================================================================ */

class MonomialMethod {
    compute(x, y) {
        const n = x.length;
        const fmt = MathFormatter;

        // Vandermonde matrix
        const V = x.map(xi => {
            const row = [];
            for (let j = 0; j < n; j++) row.push(Math.pow(xi, j));
            return row;
        });
        const coeffs = LinearSolver.solve(V, y);

        // Matrix display
        const matrixEl = document.createElement('div');
        matrixEl.id = 'matrix-section';
        let vRows = V.map(row => row.map(v => fmt.formatNumber(v)).join(' & ') + ' \\\\ ');
        let vTex = '\\begin{pmatrix}' + vRows.join('') +
            '\\end{pmatrix} \\begin{pmatrix} ' +
            Array.from({ length: n }, (_, i) => `a_${i}`).join(' \\\\ ') +
            ' \\end{pmatrix} = \\begin{pmatrix} ' +
            y.map(yy => fmt.toFraction(yy)).join(' \\\\ ') + ' \\end{pmatrix}';
        const vanDiv = document.createElement('div');
        katex.render(vTex, vanDiv, { throwOnError: false, displayMode: true });
        matrixEl.appendChild(vanDiv);

        // Polynomial display
        const polynomialEl = document.createElement('div');
        polynomialEl.id = 'polynomial-section';
        let polyTerms = [];
        for (let j = n - 1; j >= 0; j--) {
            const a = coeffs[j];
            if (Math.abs(a) < 1e-12) continue;
            let coeffTex = fmt.toFraction(a);
            if (coeffTex === '0') continue;
            let termSign = polyTerms.length === 0 ? (coeffTex.startsWith('-') ? '-' : '') : (coeffTex.startsWith('-') ? '-' : '+');
            coeffTex = coeffTex.replace(/^-/, '');
            let coeffStr = (coeffTex === '1' && j !== 0) ? '' : coeffTex;
            let varTex = j === 0 ? '' : (j === 1 ? 'x' : 'x^{' + j + '}');
            polyTerms.push(termSign + coeffStr + varTex);
        }
        let polyTex = 'p(x) = ' + (polyTerms.length ? polyTerms.join('') : '0');
        polyTex = fmt.cleanPolyTex(polyTex);
        const polyInner = document.createElement('div');
        katex.render(polyTex, polyInner, { throwOnError: false, displayMode: true });
        polynomialEl.appendChild(polyInner);

        let coeffsTex = coeffs.map((a, j) => 'a_{' + j + '} = ' + fmt.toFraction(a)).join(', ');
        const coeffsDiv = document.createElement('div');
        katex.render(coeffsTex, coeffsDiv, { throwOnError: false, displayMode: true });
        polynomialEl.appendChild(coeffsDiv);

        // Evaluator
        const pFunc = (xx) => {
            let res = 0;
            for (let j = 0; j < n; j++) res += coeffs[j] * Math.pow(xx, j);
            return isFinite(res) ? res : NaN;
        };

        return {
            pFunc,
            sections: {
                polynomial: { el: polynomialEl, available: true },
                table: { el: null, available: false },
                matrix: { el: matrixEl, available: true }
            }
        };
    }
}

class LagrangeMethod {
    compute(x, y) {
        const n = x.length;
        const fmt = MathFormatter;

        const polynomialEl = document.createElement('div');
        polynomialEl.id = 'polynomial-section';
        let polyTerms = [];
        let lPolys = [];

        for (let j = 0; j < n; j++) {
            let denom = 1;
            for (let k = 0; k < n; k++) {
                if (k !== j) {
                    const diff = x[j] - x[k];
                    if (Math.abs(diff) < 1e-12) throw new Error('Duplicate x values detected');
                    denom *= diff;
                }
            }
            let constTex = fmt.toFraction(1 / denom);
            let prodTex = '';
            for (let k = 0; k < n; k++) {
                if (k !== j) prodTex += fmt.formatTerm(x[k]);
            }
            let lTex = '\\ell_{' + j + '}(x) = ' + (Math.abs(1 / denom) === 1 ? (1 / denom < 0 ? '-' : '') : constTex);
            if (prodTex) lTex += (Math.abs(1 / denom) === 1 ? '' : '\\cdot ') + prodTex;
            lPolys.push(lTex);

            const yj = y[j];
            if (Math.abs(yj) < 1e-12) continue;
            let yTex = fmt.toFraction(yj);
            if (yTex === '0') continue;
            let termSign = polyTerms.length === 0 ? (yTex.startsWith('-') ? '-' : '') : (yTex.startsWith('-') ? '-' : '+');
            yTex = yTex.replace(/^-/, '');
            let yStr = (yTex === '1' ? '' : yTex);
            polyTerms.push(termSign + yStr + '\\ell_' + j + '(x)');
        }

        let polyTex = 'p(x) = ' + (polyTerms.length ? polyTerms.join('') : '0');
        polyTex = fmt.cleanPolyTex(polyTex);
        const polyInner = document.createElement('div');
        katex.render(polyTex, polyInner, { throwOnError: false, displayMode: true });
        polynomialEl.appendChild(polyInner);

        const cardsDiv = document.createElement('div');
        cardsDiv.className = 'flex flex-col space-y-2';
        for (let j = 0; j < n; j++) {
            const card = document.createElement('div');
            card.className = 'w-full p-4 rounded bg-gray-50';
            const fontSize = n >= 7 ? '0.8em' : '1em';
            katex.render(lPolys[j], card, { throwOnError: false, displayMode: true, output: 'html', strict: false, macros: {}, fleqn: false, trust: false, fontSize });
            cardsDiv.appendChild(card);
        }
        polynomialEl.appendChild(cardsDiv);

        const pFunc = (xx) => {
            let res = 0;
            for (let j = 0; j < n; j++) {
                let l = 1;
                for (let k = 0; k < n; k++) {
                    if (k !== j) l *= (xx - x[k]) / (x[j] - x[k]);
                }
                res += y[j] * l;
            }
            return isFinite(res) ? res : NaN;
        };

        return {
            pFunc,
            sections: {
                polynomial: { el: polynomialEl, available: true },
                table: { el: null, available: false },
                matrix: { el: null, available: false }
            }
        };
    }
}

class NewtonMethod {
    compute(x, y) {
        const n = x.length;
        const fmt = MathFormatter;

        // Divided differences
        const dd = Array.from({ length: n }, () => new Array(n).fill(0));
        for (let i = 0; i < n; i++) dd[i][0] = y[i];
        for (let k = 1; k < n; k++) {
            for (let i = 0; i < n - k; i++) {
                const diff = x[i + k] - x[i];
                if (Math.abs(diff) < 1e-12) throw new Error('Invalid divided difference due to duplicate x values');
                dd[i][k] = (dd[i + 1][k - 1] - dd[i][k - 1]) / diff;
            }
        }

        // Table
        const tableEl = document.createElement('div');
        tableEl.id = 'divided-differences-table';
        const table = document.createElement('table');
        table.className = 'min-w-full bg-white border border-gray-300';
        let headerCells = [
            '<th class="border px-4 py-2">' + katex.renderToString('x') + '</th>',
            '<th class="border px-4 py-2">' + katex.renderToString('f[\\cdot]') + '</th>'
        ];
        for (let k = 1; k < n; k++) {
            headerCells.push('<th class="border px-4 py-2">' + katex.renderToString('f[' + '\\cdot,'.repeat(k) + '\\cdot]') + '</th>');
        }
        let rows = ['<tr>' + headerCells.join('') + '</tr>'];
        for (let i = 0; i < n; i++) {
            let rowCells = ['<td class="border px-4 py-2">' + katex.renderToString('x_{' + i + '} = ' + fmt.formatNumber(x[i])) + '</td>'];
            for (let k = 0; k < n; k++) {
                if (k <= i) {
                    let style = (i === k) ? 'class="border px-4 py-2 text-red-600 font-bold"' : 'class="border px-4 py-2"';
                    rowCells.push('<td ' + style + '>' + (dd[i - k][k] !== undefined ? katex.renderToString(fmt.toFraction(dd[i - k][k])) : '') + '</td>');
                } else {
                    rowCells.push('<td class="border px-4 py-2"></td>');
                }
            }
            rows.push('<tr>' + rowCells.join('') + '</tr>');
        }
        table.innerHTML = rows.join('');
        tableEl.appendChild(table);

        // Polynomial
        const polynomialEl = document.createElement('div');
        polynomialEl.id = 'polynomial-section';
        let polyTex = 'p(x) = ';
        let terms = [];
        for (let k = 0; k < n; k++) {
            const coefNum = dd[0][k];
            if (Math.abs(coefNum) < 1e-12) continue;
            let coefTex = fmt.toFraction(coefNum);
            if (coefTex === '0') continue;
            let termSign = terms.length === 0 ? (coefTex.startsWith('-') ? '-' : '') : (coefTex.startsWith('-') ? '-' : '+');
            coefTex = coefTex.replace(/^-/, '');
            let coefStr = (coefTex === '1' && k > 0) ? '' : coefTex;
            let factors = [];
            for (let m = 0; m < k; m++) factors.push(fmt.formatTerm(x[m]));
            terms.push(termSign + coefStr + fmt.groupFactors(factors));
        }
        polyTex += terms.join('') || '0';
        polyTex = fmt.cleanPolyTex(polyTex);
        const polyInner = document.createElement('div');
        katex.render(polyTex, polyInner, { throwOnError: false, displayMode: true });
        polynomialEl.appendChild(polyInner);

        const pFunc = (xx) => {
            let res = dd[0][0];
            let prod = 1;
            for (let k = 1; k < n; k++) {
                prod *= (xx - x[k - 1]);
                res += dd[0][k] * prod;
            }
            return isFinite(res) ? res : NaN;
        };

        return {
            pFunc,
            sections: {
                polynomial: { el: polynomialEl, available: true },
                table: { el: tableEl, available: true },
                matrix: { el: null, available: false }
            }
        };
    }
}

class HermiteMethod {
    compute(x, y, { yp }) {
        const n = x.length;
        const fmt = MathFormatter;

        let z = [];
        let Q = Array.from({ length: 2 * n }, () => new Array(2 * n).fill(0));
        let pointMap = [];
        let totalRows = 0;

        for (let j = 0; j < n; j++) {
            z.push(x[j]);
            Q[totalRows][0] = y[j];
            pointMap.push(j);
            totalRows++;
            if (yp && !isNaN(yp[j])) {
                z.push(x[j]);
                Q[totalRows][0] = y[j];
                pointMap.push(j);
                totalRows++;
            }
        }

        for (let k = 1; k < totalRows; k++) {
            for (let i = 0; i < totalRows - k; i++) {
                if (Math.abs(z[i + k] - z[i]) < 1e-12) {
                    if (k === 1) {
                        Q[i][k] = yp[pointMap[i]];
                    } else {
                        throw new Error('Higher multiplicity not supported');
                    }
                } else {
                    const diff = z[i + k] - z[i];
                    if (Math.abs(diff) < 1e-12) throw new Error('Invalid divided difference due to duplicate z values');
                    Q[i][k] = (Q[i + 1][k - 1] - Q[i][k - 1]) / diff;
                }
            }
        }

        // Table
        const tableEl = document.createElement('div');
        tableEl.id = 'divided-differences-table';
        const table = document.createElement('table');
        table.className = 'min-w-full bg-white border border-gray-300';
        let headerCells = [
            '<th class="border px-4 py-2">' + katex.renderToString('z') + '</th>',
            '<th class="border px-4 py-2">' + katex.renderToString('f[\\cdot]') + '</th>'
        ];
        for (let k = 1; k < totalRows; k++) {
            headerCells.push('<th class="border px-4 py-2">' + katex.renderToString('f[' + '\\cdot,'.repeat(k) + '\\cdot]') + '</th>');
        }
        let rows = ['<tr>' + headerCells.join('') + '</tr>'];
        for (let i = 0; i < totalRows; i++) {
            let rowCells = ['<td class="border px-4 py-2">' + katex.renderToString('z_{' + i + '} = ' + fmt.formatNumber(z[i])) + '</td>'];
            for (let k = 0; k < totalRows; k++) {
                if (k <= i) {
                    let style = (i === k) ? 'class="border px-4 py-2 text-red-600 font-bold"' : 'class="border px-4 py-2"';
                    rowCells.push('<td ' + style + '>' + (Q[i - k][k] !== undefined ? katex.renderToString(fmt.toFraction(Q[i - k][k])) : '') + '</td>');
                } else {
                    rowCells.push('<td class="border px-4 py-2"></td>');
                }
            }
            rows.push('<tr>' + rowCells.join('') + '</tr>');
        }
        table.innerHTML = rows.join('');
        tableEl.appendChild(table);

        // Polynomial
        const polynomialEl = document.createElement('div');
        polynomialEl.id = 'polynomial-section';
        let polyTex = 'p(x) = ';
        let terms = [];
        for (let k = 0; k < totalRows; k++) {
            const coefNum = Q[0][k];
            if (Math.abs(coefNum) < 1e-12) continue;
            let coefTex = fmt.toFraction(coefNum);
            if (coefTex === '0') continue;
            let termSign = terms.length === 0 ? (coefTex.startsWith('-') ? '-' : '') : (coefTex.startsWith('-') ? '-' : '+');
            coefTex = coefTex.replace(/^-/, '');
            let coefStr = (coefTex === '1' && k > 0) ? '' : coefTex;
            let factors = [];
            for (let m = 0; m < k; m++) factors.push(fmt.formatTerm(z[m]));
            terms.push(termSign + coefStr + fmt.groupFactors(factors));
        }
        polyTex += terms.join('') || '0';
        polyTex = fmt.cleanPolyTex(polyTex);
        const polyInner = document.createElement('div');
        katex.render(polyTex, polyInner, { throwOnError: false, displayMode: true });
        polynomialEl.appendChild(polyInner);

        const pFunc = (xx) => {
            let res = Q[0][0] || 0;
            let prod = 1;
            for (let k = 1; k < totalRows; k++) {
                prod *= (xx - z[k - 1]);
                res += (Q[0][k] || 0) * prod;
            }
            return isFinite(res) ? res : NaN;
        };

        return {
            pFunc,
            sections: {
                polynomial: { el: polynomialEl, available: true },
                table: { el: tableEl, available: true },
                matrix: { el: null, available: false }
            }
        };
    }
}

class NaturalCubicSplineMethod {
    compute(x, y) {
        const n = x.length;
        const fmt = MathFormatter;
        if (n < 3) throw new Error('At least 3 points for cubic spline');

        const h = [];
        for (let i = 0; i < n - 1; i++) {
            h.push(x[i + 1] - x[i]);
            if (h[i] <= 0) throw new Error('Non-positive interval in cubic spline');
        }

        const nn = n - 2;
        const A = Array.from({ length: nn }, () => new Array(nn).fill(0));
        const b = new Array(nn);
        for (let ii = 0; ii < nn; ii++) {
            const i = ii + 1;
            if (ii > 0) A[ii][ii - 1] = h[i - 1];
            A[ii][ii] = 2 * (h[i - 1] + h[i]);
            if (ii < nn - 1) A[ii][ii + 1] = h[i];
            b[ii] = 6 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1]);
        }
        const mMid = LinearSolver.solve(A, b);
        const m = [0, ...mMid, 0];

        const { polynomialEl, splineFuncs } = this._buildSplineDisplay(x, y, h, m, n, fmt);

        const pFunc = this._buildEvaluator(x, n, splineFuncs);

        return {
            pFunc,
            splineFuncs,
            sections: {
                polynomial: { el: polynomialEl, available: true },
                table: { el: null, available: false },
                matrix: { el: null, available: false }
            }
        };
    }

    _buildSplineDisplay(x, y, h, m, n, fmt) {
        const polynomialEl = document.createElement('div');
        polynomialEl.id = 'polynomial-section';
        let pieceTex = 'S(x) = \\begin{cases} ';
        const splineFuncs = [];

        for (let i = 0; i < n - 1; i++) {
            const a = y[i];
            const bCoef = (y[i + 1] - y[i]) / h[i] - h[i] * (2 * m[i] + m[i + 1]) / 6;
            const c = m[i] / 2;
            const d = (m[i + 1] - m[i]) / (6 * h[i]);
            const polyTex = this._splinePieceTex(a, bCoef, c, d, x[i], fmt);
            pieceTex += polyTex + ' & x \\in [' + fmt.formatNumber(x[i]) + ', ' + fmt.formatNumber(x[i + 1]) + '] \\\\ ';
            if (i < n - 2) pieceTex += '\\\\ ';
            splineFuncs.push({ a, b: bCoef, c, d, x_i: x[i], x_ip1: x[i + 1] });
        }

        pieceTex += '\\end{cases}';
        const pieceInner = document.createElement('div');
        katex.render(pieceTex, pieceInner, { throwOnError: false, displayMode: true });
        polynomialEl.appendChild(pieceInner);

        return { polynomialEl, splineFuncs };
    }

    _splinePieceTex(a, bCoef, c, d, xi, fmt) {
        let polyTerms = [];
        if (Math.abs(d) > 1e-12) {
            let dTex = fmt.toFraction(d);
            let termSign = dTex.startsWith('-') ? '-' : (polyTerms.length ? '+' : '');
            dTex = dTex.replace(/^-/, '');
            let dStr = dTex === '1' ? '' : dTex;
            polyTerms.push(termSign + dStr + fmt.formatTerm(xi) + '^{3}');
        }
        if (Math.abs(c) > 1e-12) {
            let cTex = fmt.toFraction(c);
            let termSign = cTex.startsWith('-') ? '-' : (polyTerms.length ? '+' : '');
            cTex = cTex.replace(/^-/, '');
            let cStr = cTex === '1' ? '' : cTex;
            polyTerms.push(termSign + cStr + fmt.formatTerm(xi) + '^{2}');
        }
        if (Math.abs(bCoef) > 1e-12) {
            let bTex = fmt.toFraction(bCoef);
            let termSign = bTex.startsWith('-') ? '-' : (polyTerms.length ? '+' : '');
            bTex = bTex.replace(/^-/, '');
            let bStr = bTex === '1' ? '' : bTex;
            polyTerms.push(termSign + bStr + fmt.formatTerm(xi));
        }
        if (Math.abs(a) > 1e-12 || polyTerms.length === 0) {
            let aTex = fmt.toFraction(a);
            let termSign = aTex.startsWith('-') ? '-' : (polyTerms.length ? '+' : '');
            aTex = aTex.replace(/^-/, '');
            polyTerms.push(termSign + aTex);
        }
        let tex = polyTerms.join('');
        tex = fmt.cleanPolyTex(tex);
        if (tex.startsWith('+')) tex = tex.slice(1);
        return tex;
    }

    _buildEvaluator(x, n, splineFuncs) {
        return (xx) => {
            let i;
            if (xx < x[0]) { i = 0; }
            else if (xx > x[n - 1]) { i = n - 2; }
            else { i = 0; for (; i < n - 1; i++) { if (xx <= x[i + 1]) break; } }
            const dx = xx - x[i];
            const { a, b, c, d } = splineFuncs[i];
            const res = a + b * dx + c * dx * dx + d * dx * dx * dx;
            return isFinite(res) ? res : NaN;
        };
    }
}

class ClampedCubicSplineMethod extends NaturalCubicSplineMethod {
    compute(x, y, { yp0, ypn }) {
        const n = x.length;
        const fmt = MathFormatter;
        if (n < 3) throw new Error('At least 3 points for clamped cubic spline');

        const h = [];
        for (let i = 0; i < n - 1; i++) {
            h.push(x[i + 1] - x[i]);
            if (h[i] <= 0) throw new Error('Non-positive interval in cubic spline');
        }

        const A = Array.from({ length: n }, () => new Array(n).fill(0));
        const b = new Array(n);
        A[0][0] = 2 * h[0];
        A[0][1] = h[0];
        b[0] = 6 * ((y[1] - y[0]) / h[0] - yp0);
        for (let i = 1; i < n - 1; i++) {
            A[i][i - 1] = h[i - 1];
            A[i][i] = 2 * (h[i - 1] + h[i]);
            A[i][i + 1] = h[i];
            b[i] = 6 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1]);
        }
        A[n - 1][n - 2] = h[n - 2];
        A[n - 1][n - 1] = 2 * h[n - 2];
        b[n - 1] = 6 * (ypn - (y[n - 1] - y[n - 2]) / h[n - 2]);
        const m = LinearSolver.solve(A, b);

        const { polynomialEl, splineFuncs } = this._buildSplineDisplay(x, y, h, m, n, fmt);
        const pFunc = this._buildEvaluator(x, n, splineFuncs);

        return {
            pFunc,
            splineFuncs,
            sections: {
                polynomial: { el: polynomialEl, available: true },
                table: { el: null, available: false },
                matrix: { el: null, available: false }
            }
        };
    }
}

/* ================================================================
   InterpolationPlotter
   ================================================================ */
class InterpolationPlotter {
    constructor(plotEl) {
        this.plotEl = plotEl;
    }

    plot({ x, y, yp, sampleX, pY, funcY, plotRange, method }) {
        const n = x.length;
        this.plotEl.innerHTML = '';

        let allY = [...y, ...pY.filter(isFinite)];
        if (funcY) allY.push(...funcY.filter(isFinite));
        if (allY.length === 0) throw new Error('No valid y values for plotting');

        let ymin = Math.min(...allY);
        let ymax = Math.max(...allY);
        let ybuf = 0.05 * (ymax - ymin);
        const minYRange = 0.2;
        if (ymax - ymin < minYRange) {
            const mid = (ymax + ymin) / 2;
            ymin = mid - minYRange / 2;
            ymax = mid + minYRange / 2;
            ybuf = 0;
        } else {
            if (ybuf === 0) ybuf = 0.1;
            ymin -= ybuf;
            ymax += ybuf;
        }

        const width = 400, height = 300;
        const margin = { top: 20, right: 120, bottom: 30, left: 50 };
        const svg = d3.select(this.plotEl).append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left}, ${margin.top})`);

        const xScale = d3.scaleLinear().domain(plotRange).range([0, width]);
        const yScale = d3.scaleLinear().domain([ymin, ymax]).range([height, 0]);

        // Background
        svg.append('rect').attr('width', width).attr('height', height).attr('fill', '#f7f7f7');

        // Grid
        svg.append('g').attr('class', 'grid').attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale).tickSize(-height).tickFormat(''));
        svg.append('g').attr('class', 'grid')
            .call(d3.axisLeft(yScale).tickSize(-width).tickFormat(''));

        // Axes
        svg.append('g').attr('transform', `translate(0, ${height})`).call(d3.axisBottom(xScale));
        svg.append('g').call(d3.axisLeft(yScale));

        // Interpolant curve
        const isSpline = method === 'cubic_spline' || method === 'clamped_cubic_spline';
        if (isSpline) {
            for (let i = 0; i < n - 1; i++) {
                const subX = sampleX.filter(sx => sx >= x[i] && sx <= x[i + 1]);
                const subY = pY.slice(sampleX.indexOf(subX[0]), sampleX.indexOf(subX[0]) + subX.length);
                const line = d3.line()
                    .x((d, j) => xScale(subX[j]))
                    .y((d, j) => yScale(subY[j]))
                    .defined((d, j) => isFinite(subY[j]));
                svg.append('path').datum(subY).attr('fill', 'none')
                    .attr('stroke', 'blue').attr('stroke-width', 1.5).attr('d', line);
            }
        } else {
            const line = d3.line()
                .x((d, i) => xScale(sampleX[i]))
                .y((d, i) => yScale(pY[i]))
                .defined((d, i) => isFinite(pY[i]));
            svg.append('path').datum(pY).attr('fill', 'none')
                .attr('stroke', 'blue').attr('stroke-width', 1.5).attr('d', line);
        }

        // Data points
        svg.selectAll('circle').data(x).enter().append('circle')
            .attr('cx', d => xScale(d))
            .attr('cy', (d, i) => yScale(y[i]))
            .attr('r', 5).attr('fill', 'red').attr('stroke', '#111');

        // Original function
        if (funcY) {
            const funcLine = d3.line()
                .x((d, i) => xScale(sampleX[i]))
                .y((d, i) => yScale(funcY[i]))
                .defined((d, i) => isFinite(funcY[i]));
            svg.append('path').datum(funcY).attr('fill', 'none')
                .attr('stroke', 'red').attr('stroke-width', 1.5).attr('stroke-dasharray', '5,5').attr('d', funcLine);
        }

        // Hermite slopes
        let hasSlope = false;
        if (method === 'hermite' && yp) {
            const dx = (plotRange[1] - plotRange[0]) / 50;
            yp.forEach((slope, j) => {
                if (!isNaN(slope) && isFinite(slope)) {
                    hasSlope = true;
                    const lineX = [x[j] - dx, x[j] + dx];
                    const lineY = [y[j] - dx * slope, y[j] + dx * slope];
                    const slopeLine = d3.line()
                        .x((d, i) => xScale(lineX[i]))
                        .y((d, i) => yScale(lineY[i]));
                    svg.append('path').datum([0, 1]).attr('fill', 'none')
                        .attr('stroke', 'black').attr('stroke-width', 1.5).attr('d', slopeLine);
                }
            });
        }

        // Legend
        const legend = svg.append('g').attr('transform', `translate(${width + 20}, 0)`);
        let legY = 0;
        legend.append('rect').attr('x', 0).attr('y', legY).attr('width', 10).attr('height', 10).attr('fill', 'blue');
        legend.append('text').attr('x', 15).attr('y', legY + 8).text('Interpolant');
        legY += 20;
        legend.append('circle').attr('cx', 5).attr('cy', legY + 5).attr('r', 5).attr('fill', 'red').attr('stroke', '#111');
        legend.append('text').attr('x', 15).attr('y', legY + 8).text('Points');
        legY += 20;
        if (funcY) {
            legend.append('line').attr('x1', 0).attr('y1', legY + 5).attr('x2', 10).attr('y2', legY + 5)
                .attr('stroke', 'red').attr('stroke-width', 1.5).attr('stroke-dasharray', '5,5');
            legend.append('text').attr('x', 15).attr('y', legY + 8).text('Function');
            legY += 20;
        }
        if (hasSlope) {
            legend.append('line').attr('x1', 0).attr('y1', legY + 5).attr('x2', 10).attr('y2', legY + 5)
                .attr('stroke', 'black').attr('stroke-width', 1.5);
            legend.append('text').attr('x', 15).attr('y', legY + 8).text('Slopes');
        }
    }

    downloadPNG() {
        const svgElement = this.plotEl.querySelector('svg');
        if (!svgElement) return;
        const svgData = new XMLSerializer().serializeToString(svgElement);
        const canvas = document.createElement('canvas');
        const svgSize = svgElement.getBoundingClientRect();
        canvas.width = svgSize.width;
        canvas.height = svgSize.height;
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.onload = function () {
            ctx.drawImage(img, 0, 0);
            const pngFile = canvas.toDataURL('image/png');
            const downloadLink = document.createElement('a');
            downloadLink.download = 'interpolation_graph.png';
            downloadLink.href = pngFile;
            downloadLink.click();
        };
        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
    }
}

/* ================================================================
   InterpolationApp – top-level controller
   ================================================================ */
class InterpolationApp {
    constructor() {
        this.methods = {
            monomial: new MonomialMethod(),
            lagrange: new LagrangeMethod(),
            newton: new NewtonMethod(),
            hermite: new HermiteMethod(),
            cubic_spline: new NaturalCubicSplineMethod(),
            clamped_cubic_spline: new ClampedCubicSplineMethod()
        };
        this.selectedMethod = 'monomial';
        this.selectedNodeType = 'equispaced';
        this.pFunc = null;
        this.originalFunc = null;
        this.dom = {};
        this.plotter = null;
    }

    init() {
        this._cacheDom();
        this.plotter = new InterpolationPlotter(this.dom.plot);
        this._bindEvents();
        this._setInitialActive();
        this.updateInputDisplay();
        renderMathInElement(document.body, {
            delimiters: [
                { left: "$$", right: "$$", display: true },
                { left: "$", right: "$", display: false }
            ],
            throwOnError: false
        });
    }

    /* ---- DOM ---- */
    _cacheDom() {
        const id = (s) => document.getElementById(s);
        this.dom = {
            output: id('output'),
            outputToggles: id('output-toggles'),
            downloadContainer: id('download-container'),
            evalContainer: id('eval-container'),
            evalOutput: id('eval-output'),
            plot: id('plot'),
            xValues: id('x_values'),
            fValues: id('f_values'),
            fpValues: id('fp_values'),
            endpointFpValues: id('endpoint_fp_values'),
            fpInput: id('fp_input'),
            endpointFpInput: id('endpoint_fp_input'),
            funcStr: id('func_str'),
            a: id('a'),
            b: id('b'),
            nPoints: id('n_points'),
            showPolynomial: id('show_polynomial'),
            showTable: id('show_table'),
            showMatrix: id('show_matrix'),
            showPoints: id('show_points'),
            evalX: id('eval_x'),
            downloadBtn: id('download-btn'),
            evalBtn: id('eval-btn'),
            custom: id('custom'),
            functionRadio: id('function'),
            customInputs: id('custom-inputs'),
            functionInputs: id('function-inputs')
        };
    }

    /* ---- Events ---- */
    _bindEvents() {
        this.dom.custom.addEventListener('change', () => this.updateInputDisplay());
        this.dom.functionRadio.addEventListener('change', () => this.updateInputDisplay());

        document.querySelectorAll('.method-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.method-btn').forEach(b => {
                    b.classList.remove('text-white', 'bg-gradient-to-br', 'from-purple-600', 'to-blue-500');
                    b.classList.add('bg-white', 'text-black', 'border', 'border-gray-300');
                });
                btn.classList.remove('bg-white', 'text-black', 'border', 'border-gray-300');
                btn.classList.add('text-white', 'bg-gradient-to-br', 'from-purple-600', 'to-blue-500');
                this.selectedMethod = btn.dataset.method;
                this.updateInputDisplay();
            });
        });

        document.querySelectorAll('.node-type-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.node-type-btn').forEach(b => {
                    b.classList.remove('text-white', 'bg-gradient-to-br', 'from-purple-600', 'to-blue-500');
                    b.classList.add('bg-white', 'text-black', 'border', 'border-gray-300');
                });
                btn.classList.remove('bg-white', 'text-black', 'border', 'border-gray-300');
                btn.classList.add('text-white', 'bg-gradient-to-br', 'from-purple-600', 'to-blue-500');
                this.selectedNodeType = btn.dataset.nodeType;
            });
        });

        this.dom.downloadBtn.addEventListener('click', () => this.plotter.downloadPNG());
        this.dom.evalBtn.addEventListener('click', () => this.evaluate());

        this._bindExamples();
    }

    _setInitialActive() {
        const mono = document.querySelector('[data-method="monomial"]');
        mono.classList.remove('bg-white', 'text-black', 'border', 'border-gray-300');
        mono.classList.add('text-white', 'bg-gradient-to-br', 'from-purple-600', 'to-blue-500');
        const equi = document.querySelector('[data-node-type="equispaced"]');
        equi.classList.remove('bg-white', 'text-black', 'border', 'border-gray-300');
        equi.classList.add('text-white', 'bg-gradient-to-br', 'from-purple-600', 'to-blue-500');
    }

    /* ---- Examples ---- */
    _bindExamples() {
        document.getElementById('example-points-data').addEventListener('click', () => {
            this.dom.custom.checked = true;
            this.updateInputDisplay();
            this.dom.xValues.value = '-1, 0, 1, 2, 3';
            this.dom.fValues.value = '0, -8, -2, 0, 4';
            document.querySelector('[data-method="lagrange"]').click();
        });

        document.getElementById('example-runge').addEventListener('click', () => {
            this.dom.functionRadio.checked = true;
            this.updateInputDisplay();
            this.dom.funcStr.value = '1/(1+25*x^2)';
            this.dom.a.value = '-1';
            this.dom.b.value = '1';
            this.dom.nPoints.value = '11';
            document.querySelector('[data-method="lagrange"]').click();
            document.querySelector('[data-node-type="equispaced"]').click();
        });

        document.getElementById('example-hermite-func').addEventListener('click', () => {
            this.dom.functionRadio.checked = true;
            this.updateInputDisplay();
            this.dom.funcStr.value = 'exp(-x)*cos(5*x)';
            this.dom.a.value = '0';
            this.dom.b.value = '3';
            this.dom.nPoints.value = '6';
            document.querySelector('[data-method="hermite"]').click();
            document.querySelector('[data-node-type="equispaced"]').click();
        });

        document.getElementById('example-newton-func').addEventListener('click', () => {
            this.dom.functionRadio.checked = true;
            this.updateInputDisplay();
            this.dom.funcStr.value = 'exp(-x)*cos(5*x)';
            this.dom.a.value = '0';
            this.dom.b.value = '3';
            this.dom.nPoints.value = '6';
            document.querySelector('[data-method="newton"]').click();
            document.querySelector('[data-node-type="equispaced"]').click();
        });

        document.getElementById('example-spline').addEventListener('click', () => {
            this.dom.functionRadio.checked = true;
            this.updateInputDisplay();
            this.dom.funcStr.value = '1/(1+25*x^2)';
            this.dom.a.value = '-1';
            this.dom.b.value = '1';
            this.dom.nPoints.value = '11';
            document.querySelector('[data-method="cubic_spline"]').click();
            document.querySelector('[data-node-type="equispaced"]').click();
        });
    }

    /* ---- UI State ---- */
    updateInputDisplay() {
        if (this.dom.custom.checked) {
            this.dom.functionInputs.style.display = 'none';
            this.dom.customInputs.style.display = 'block';
        } else {
            this.dom.customInputs.style.display = 'none';
            this.dom.functionInputs.style.display = 'block';
        }
        const isHermite = this.selectedMethod === 'hermite';
        const isClamped = this.selectedMethod === 'clamped_cubic_spline';
        this.dom.fpInput.classList.toggle('hidden', !isHermite || !this.dom.custom.checked);
        this.dom.endpointFpInput.classList.toggle('hidden', !isClamped || !this.dom.custom.checked);
        this.dom.output.innerHTML = '';
        this.dom.plot.innerHTML = '';
        this.dom.downloadContainer.classList.add('hidden');
        this.dom.evalContainer.classList.add('hidden');
        this.dom.evalOutput.innerHTML = '';
        this.pFunc = null;
        this.originalFunc = null;
    }

    clearAll() {
        this.dom.xValues.value = '';
        this.dom.fValues.value = '';
        this.dom.fpValues.value = '';
        this.dom.endpointFpValues.value = '';
        this.dom.funcStr.value = 'sin(x)';
        this.dom.a.value = '-5';
        this.dom.b.value = '5';
        this.dom.nPoints.value = '5';
        this.dom.output.innerHTML = '';
        this.dom.plot.innerHTML = '';
        this.dom.outputToggles.classList.add('hidden');
        this.dom.downloadContainer.classList.add('hidden');
        this.dom.evalContainer.classList.add('hidden');
        this.dom.evalOutput.innerHTML = '';
        this.pFunc = null;
        this.originalFunc = null;
        this.updateInputDisplay();
    }

    /* ---- Input parsing ---- */
    _parseExpression(expr, label) {
        const val = math.evaluate(expr);
        if (isNaN(val) || !isFinite(val)) throw new Error(`Invalid ${label}: ${expr}`);
        return val;
    }

    _parseExpressionList(str, label) {
        return str.split(',').map(s => {
            const expr = s.trim();
            try {
                return this._parseExpression(expr, label);
            } catch (e) {
                throw new Error(`Invalid ${label} expression: ${expr}. Use valid math expressions like pi/6, sin(pi/3), or exp(2).`);
            }
        });
    }

    _readInputs() {
        const method = this.selectedMethod;
        const inputType = document.querySelector('input[name="input_type"]:checked').value;
        let x = [], y = [], yp = null, yp0, ypn, func = null, rangeA, rangeB;

        if (inputType === 'custom') {
            const xStr = this.dom.xValues.value.trim();
            const yStr = this.dom.fValues.value.trim();
            if (!xStr || !yStr) throw new Error('Please enter x and f(x) values');

            x = this._parseExpressionList(xStr, 'x value');
            y = this._parseExpressionList(yStr, 'f(x) value');

            if (x.length !== y.length || x.length < 2 || x.length > 16) {
                throw new Error('Invalid number of points. Must be 2-16 and same length');
            }
            const uniqueX = new Set(x.map(v => v.toFixed(10)));
            if (uniqueX.size !== x.length && (method === 'lagrange' || method === 'newton')) {
                throw new Error('Duplicate x values not allowed for Lagrange or Newton');
            }
            if (method === 'hermite' && !this.dom.fpInput.classList.contains('hidden')) {
                const ypStr = this.dom.fpValues.value.trim();
                yp = ypStr ? ypStr.split(',').map(s => {
                    const expr = s.trim();
                    if (expr === '') return NaN;
                    return this._parseExpression(expr, "f'(x) value");
                }) : new Array(x.length).fill(NaN);
                if (yp.length !== x.length) throw new Error("f'(x) must have same length as x and f(x)");
            }
            if (method === 'clamped_cubic_spline' && !this.dom.endpointFpInput.classList.contains('hidden')) {
                const ypStr = this.dom.endpointFpValues.value.trim();
                const endpointYp = this._parseExpressionList(ypStr, 'endpoint derivative');
                if (endpointYp.length !== 2) throw new Error('Endpoint derivatives: must be two expressions separated by comma');
                yp0 = endpointYp[0];
                ypn = endpointYp[1];
            }
        } else {
            const funcStr = this.dom.funcStr.value.trim();
            rangeA = this._parseExpression(this.dom.a.value.trim(), 'range start');
            rangeB = this._parseExpression(this.dom.b.value.trim(), 'range end');
            const nPoints = parseInt(this.dom.nPoints.value);

            if (rangeA >= rangeB || nPoints < 2 || nPoints > 16) throw new Error('Invalid range or number of points');

            func = (xx) => math.evaluate(funcStr, { x: xx });
            const testVal = func(rangeA);
            if (isNaN(testVal) || !isFinite(testVal)) throw new Error('Function evaluation failed');

            if (this.selectedNodeType === 'equispaced') {
                const step = (rangeB - rangeA) / (nPoints - 1);
                for (let i = 0; i < nPoints; i++) x.push(rangeA + i * step);
            } else {
                for (let k = 0; k < nPoints; k++) {
                    x.push((rangeA + rangeB) / 2 + (rangeB - rangeA) / 2 * Math.cos(Math.PI * (2 * k + 1) / (2 * nPoints)));
                }
                x.sort((a, b) => a - b);
            }

            y = x.map(xi => {
                const val = func(xi);
                if (isNaN(val) || !isFinite(val)) throw new Error('Function evaluation produced invalid result at x=' + xi);
                return val;
            });

            if (method === 'hermite') {
                try {
                    const node = math.parse(funcStr);
                    const deriv = math.derivative(node, 'x');
                    yp = x.map(xi => {
                        const val = deriv.evaluate({ x: xi });
                        if (isNaN(val) || !isFinite(val)) throw new Error('Derivative evaluation failed');
                        return val;
                    });
                } catch {
                    const h = 1e-6;
                    yp = x.map(xi => (func(xi + h) - func(xi - h)) / (2 * h));
                }
            }
            if (method === 'clamped_cubic_spline') {
                try {
                    const node = math.parse(funcStr);
                    const deriv = math.derivative(node, 'x');
                    yp0 = deriv.evaluate({ x: x[0] });
                    ypn = deriv.evaluate({ x: x[x.length - 1] });
                } catch {
                    const h = 1e-6;
                    yp0 = (func(x[0] + h) - func(x[0] - h)) / (2 * h);
                    ypn = (func(x[x.length - 1] + h) - func(x[x.length - 1] - h)) / (2 * h);
                }
            }
            this.originalFunc = func;
        }

        // Sort by x
        const indices = x.map((_, idx) => idx).sort((a, b) => x[a] - x[b]);
        x = indices.map(i => x[i]);
        y = indices.map(i => y[i]);
        if (yp) yp = indices.map(i => yp[i]);

        let plotRange = [x[0], x[x.length - 1]];
        if (inputType === 'function' && func) {
            plotRange[0] = Math.max(x[0], rangeA);
            plotRange[1] = Math.min(x[x.length - 1], rangeB);
        }

        return { x, y, yp, yp0, ypn, func, plotRange, inputType, method };
    }

    /* ---- Main compute ---- */
    compute() {
        const output = this.dom.output;
        output.innerHTML = '<div class="text-red-500">Computing...</div>';
        this.dom.outputToggles.classList.add('hidden');
        this.dom.downloadContainer.classList.add('hidden');
        this.dom.evalContainer.classList.add('hidden');
        this.dom.evalOutput.innerHTML = '';
        this.pFunc = null;
        this.originalFunc = null;

        try {
            const data = this._readInputs();
            const { x, y, yp, yp0, ypn, plotRange, inputType, method } = data;
            const n = x.length;
            output.innerHTML = '';

            // Points display
            const pointsDiv = document.createElement('div');
            pointsDiv.id = 'points-section';
            pointsDiv.style.display = 'none';
            const pointsTex = x.map((xi, i) => `\\left(${MathFormatter.formatNumber(xi)}, ${MathFormatter.toFraction(y[i])}\\right)`).join(' \\quad ');
            katex.render(pointsTex, pointsDiv, { throwOnError: false, displayMode: true });
            output.appendChild(pointsDiv);

            // Delegate to strategy
            const strategy = this.methods[method];
            const result = strategy.compute(x, y, { yp, yp0, ypn });
            this.pFunc = result.pFunc;
            const { polynomial, table, matrix } = result.sections;

            // Append output sections
            if (matrix.available) output.appendChild(matrix.el);
            if (polynomial.available) output.appendChild(polynomial.el);
            if (table.available) output.appendChild(table.el);

            // Toggles
            this._setupToggles({
                hasPolynomial: polynomial.available,
                hasTable: table.available,
                hasMatrix: matrix.available,
                hasPoints: true,
                polynomialEl: polynomial.el,
                tableEl: table.el,
                matrixEl: matrix.el,
                pointsEl: pointsDiv
            });

            // Plot
            if (this.pFunc) {
                const numSamplesPerInterval = 50;
                let sampleX = [];
                let pY = [];
                const isSpline = method === 'cubic_spline' || method === 'clamped_cubic_spline';

                if (isSpline) {
                    for (let i = 0; i < n - 1; i++) {
                        const subX = d3.range(x[i], x[i + 1], (x[i + 1] - x[i]) / numSamplesPerInterval);
                        if (i === n - 2) subX.push(x[i + 1]);
                        sampleX.push(...subX);
                        pY.push(...subX.map(xx => this.pFunc(xx)));
                    }
                } else {
                    sampleX = d3.range(plotRange[0], plotRange[1], (plotRange[1] - plotRange[0]) / (numSamplesPerInterval * (n - 1)));
                    if (!sampleX.includes(plotRange[1])) sampleX.push(plotRange[1]);
                    pY = sampleX.map(xx => this.pFunc(xx));
                }

                let funcY = null;
                if (this.originalFunc && inputType === 'function') {
                    funcY = sampleX.map(xi => {
                        const val = this.originalFunc(xi);
                        return isFinite(val) ? val : NaN;
                    });
                }

                this.plotter.plot({ x, y, yp, sampleX, pY, funcY, plotRange, method });
                this.dom.downloadContainer.classList.remove('hidden');
                this.dom.evalContainer.classList.remove('hidden');
            }
        } catch (e) {
            console.error('Error in computeInterpolation:', e);
            output.innerHTML = '<div class="text-red-500">Error: ' + e.message + '</div>';
        }
    }

    _setupToggles({ hasPolynomial, hasTable, hasMatrix, hasPoints, polynomialEl, tableEl, matrixEl, pointsEl }) {
        this.dom.outputToggles.classList.remove('hidden');
        const bind = (checkbox, has, el) => {
            checkbox.parentElement.classList.toggle('hidden', !has);
            if (has && el) {
                el.style.display = checkbox.checked ? 'block' : 'none';
                checkbox.onchange = () => { el.style.display = checkbox.checked ? 'block' : 'none'; };
            }
        };
        bind(this.dom.showPolynomial, hasPolynomial, polynomialEl);
        bind(this.dom.showTable, hasTable, tableEl);
        bind(this.dom.showMatrix, hasMatrix, matrixEl);
        bind(this.dom.showPoints, hasPoints, pointsEl);
    }

    /* ---- Evaluation ---- */
    evaluate() {
        if (!this.pFunc) {
            this.dom.evalOutput.innerHTML = '<div class="text-red-500">Compute interpolation first</div>';
            return;
        }
        const evalStr = this.dom.evalX.value.trim();
        if (!evalStr) {
            this.dom.evalOutput.innerHTML = '<div class="text-red-500">Enter x values</div>';
            return;
        }

        let evalX;
        try {
            evalX = evalStr.split(',').map(s => {
                const val = math.evaluate(s.trim());
                if (isNaN(val) || !isFinite(val)) throw new Error('Invalid x value');
                return val;
            });
        } catch {
            this.dom.evalOutput.innerHTML = '<div class="text-red-500">Invalid x values</div>';
            return;
        }

        const evalY = evalX.map(xx => this.pFunc(xx));
        const fmt = MathFormatter;
        let tableHTML;

        if (this.originalFunc) {
            const errors = evalX.map(xx => Math.abs(this.originalFunc(xx) - this.pFunc(xx)));
            tableHTML = `
                <div class="flex justify-center space-x-8">
                    <table class="border-collapse border border-gray-300">
                        <thead><tr><th colspan="2" class="border px-4 py-2">Point evaluations</th></tr></thead>
                        <tbody>
                            ${evalX.map((xx, i) => `<tr><td class="border px-4 py-2">$p(${fmt.formatNumber(xx)})$</td><td class="border px-4 py-2">$  ${fmt.toFraction(evalY[i])} $</td></tr>`).join('')}
                        </tbody>
                    </table>
                    <table class="border-collapse border border-gray-300">
                        <thead><tr><th colspan="2" class="border px-4 py-2">Absolute errors</th></tr></thead>
                        <tbody>
                            ${evalX.map((xx, i) => `<tr><td class="border px-4 py-2">$|f(${fmt.formatNumber(xx)}) - p(${fmt.formatNumber(xx)})|$</td><td class="border px-4 py-2">$  ${fmt.toFraction(errors[i])} $</td></tr>`).join('')}
                        </tbody>
                    </table>
                </div>`;
        } else {
            tableHTML = `
                <table class="border-collapse border border-gray-300 mx-auto">
                    <thead><tr><th colspan="2" class="border px-4 py-2">Point evaluations</th></tr></thead>
                    <tbody>
                        ${evalX.map((xx, i) => `<tr><td class="border px-4 py-2">$p(${fmt.formatNumber(xx)})$</td><td class="border px-4 py-2">$  ${fmt.toFraction(evalY[i])} $</td></tr>`).join('')}
                    </tbody>
                </table>`;
        }

        this.dom.evalOutput.innerHTML = tableHTML;
        renderMathInElement(this.dom.evalOutput, {
            delimiters: [
                { left: "$$", right: "$$", display: true },
                { left: "$", right: "$", display: false }
            ],
            throwOnError: false
        });
    }
}

/* ================================================================
   Bootstrap
   ================================================================ */
let app;
window.onload = function () {
    app = new InterpolationApp();
    app.init();
};

/* Global callbacks referenced by onclick in the HTML */
function computeInterpolation() { app.compute(); }
function clearAll() { app.clearAll(); }
