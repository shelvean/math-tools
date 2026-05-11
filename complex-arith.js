/* ============================================================
 *  complex-arith.js
 *  Shared Complex-number support for the linear-algebra tools.
 *
 *  Exposes (on the global scope, browser-only):
 *    - Complex            class with add/sub/mul/div/neg/inv/abs/sqrt/conj …
 *    - parseFraction(s)   -> Number  (real "1/2", "0.5", "3" …)
 *    - parseComplex(s)    -> Complex (real or "2+3i", "-1/2-i", "0.2i" …)
 *    - toFraction(x)      -> "p/q" string for a real x
 *    - toLatexComplex(z, decimals, mode) -> KaTeX/MathJax string
 *    - isZeroLike(x)      -> works on number or Complex
 * ============================================================ */
(function (root) {
  'use strict';

  function trimTrailingZeros(s) {
    return s.replace(/(\.\d*?[1-9])0+$/, '$1')
            .replace(/\.0+$/, '')
            .replace(/(\d)\.$/, '$1');
  }

  function parseFraction(str) {
    if (str === null || str === undefined) return NaN;
    str = String(str).trim().replace(/−/g, '-');
    if (str === '') return 0;
    if (/^[+-]?(\d*\.)?\d+([eE][+-]?\d+)?$/.test(str)) return parseFloat(str);
    if (/^[+-]?\d+\/\d+$/.test(str)) {
      var parts = str.split('/');
      var den = +parts[1];
      if (den === 0) return NaN;
      return +parts[0] / den;
    }
    var f = parseFloat(str);
    if (!isNaN(f)) return f;
    return NaN;
  }

  function toFraction(x, tolerance, maxIterations) {
    tolerance = tolerance || 1e-6;
    maxIterations = maxIterations || 20;
    if (!isFinite(x) || isNaN(x)) return 'nan';
    if (Math.abs(x) < 1e-10) return '0';
    var sign = x < 0 ? '-' : '';
    x = Math.abs(x);
    var h1 = 1, h2 = 0, k1 = 0, k2 = 1, b = x;
    for (var i = 0; i < maxIterations; i++) {
      var a = Math.floor(b);
      var h = a * h1 + h2;
      var k = a * k1 + k2;
      if (Math.abs(x - h / k) < tolerance) {
        return k === 1 ? sign + h : sign + h + '/' + k;
      }
      h2 = h1; h1 = h; k2 = k1; k1 = k;
      if (b - a === 0) break;
      b = 1 / (b - a);
    }
    return k1 === 1 ? sign + h1 : sign + h1 + '/' + k1;
  }

  function formatImaginaryFraction(im) {
    if (im === '0') return '';
    var isNeg = (im[0] === '-');
    var frac = isNeg ? im.slice(1) : im;
    var parts = frac.split('/');
    if (parts.length === 1) {
      if (Math.abs(+parts[0] - 1) < 1e-10) return isNeg ? '-i' : 'i';
      return (isNeg ? '-' : '') + parts[0] + 'i';
    }
    var numerator = parts[0], denominator = parts[1];
    if (Math.abs(+numerator) === 1) {
      return (isNeg ? '-' : '') + 'i/' + denominator;
    }
    return (isNeg ? '-' : '') + numerator + 'i/' + denominator;
  }

  function Complex(re, im) {
    if (!(this instanceof Complex)) return new Complex(re, im);
    this.re = +re || 0;
    this.im = +im || 0;
  }

  Complex.parse = function (str) {
    if (str instanceof Complex) return str.clone();
    if (typeof str === 'number') return new Complex(str, 0);
    var s = String(str).replace(/\s+/g, '').replace(/−/g, '-');
    if (!s) return new Complex(0, 0);
    if (/^[-+]?i$/.test(s)) return new Complex(0, s[0] === '-' ? -1 : 1);
    var re = 0, im = 0;
    s = s.replace(/([\+\-]|^)(i)/g, function (m, p1) { return p1 + '1i'; });
    if (!s.includes('i')) {
      re = parseFraction(s);
      if (isNaN(re)) throw new Error('Invalid number: ' + str);
      im = 0;
    } else if (s.endsWith('i')) {
      var parts = s.split(/(?=[+\-][^+\-]*i?$)/g).filter(Boolean);
      for (var k = 0; k < parts.length; k++) {
        var part = parts[k];
        if (part.endsWith('i')) {
          var v = parseFraction(part.slice(0, -1));
          if (isNaN(v)) throw new Error('Invalid imaginary part: ' + str);
          im += v;
        } else {
          var r = parseFraction(part);
          if (isNaN(r)) throw new Error('Invalid real part: ' + str);
          re += r;
        }
      }
    } else {
      throw new Error('Invalid complex literal: ' + str);
    }
    return new Complex(re, im);
  };

  Complex.from = function (x) {
    if (x instanceof Complex) return x;
    if (typeof x === 'number') return new Complex(x, 0);
    if (x && typeof x === 'object' && 're' in x && 'im' in x) return new Complex(x.re, x.im);
    return Complex.parse(x);
  };

  Complex.zero = function () { return new Complex(0, 0); };
  Complex.one  = function () { return new Complex(1, 0); };
  Complex.I    = function () { return new Complex(0, 1); };

  Complex.prototype.clone = function () { return new Complex(this.re, this.im); };
  Complex.prototype.add   = function (b) { b = Complex.from(b); return new Complex(this.re + b.re, this.im + b.im); };
  Complex.prototype.sub   = function (b) { b = Complex.from(b); return new Complex(this.re - b.re, this.im - b.im); };
  Complex.prototype.neg   = function () { return new Complex(-this.re, -this.im); };
  Complex.prototype.mul   = function (b) {
    b = Complex.from(b);
    return new Complex(this.re * b.re - this.im * b.im,
                       this.re * b.im + this.im * b.re);
  };
  Complex.prototype.div   = function (b) {
    b = Complex.from(b);
    var den = b.re * b.re + b.im * b.im;
    if (den === 0) throw new Error('Division by zero');
    return new Complex((this.re * b.re + this.im * b.im) / den,
                       (this.im * b.re - this.re * b.im) / den);
  };
  Complex.prototype.inv   = function () {
    var den = this.re * this.re + this.im * this.im;
    if (den === 0) throw new Error('Division by zero in inverse');
    return new Complex(this.re / den, -this.im / den);
  };
  Complex.prototype.conj  = function () { return new Complex(this.re, -this.im); };
  Complex.prototype.abs   = function () { return Math.hypot(this.re, this.im); };
  Complex.prototype.abs2  = function () { return this.re * this.re + this.im * this.im; };
  Complex.prototype.arg   = function () { return Math.atan2(this.im, this.re); };

  Complex.prototype.sqrt = function () {
    // Principal branch
    if (this.im === 0) {
      if (this.re >= 0) return new Complex(Math.sqrt(this.re), 0);
      return new Complex(0, Math.sqrt(-this.re));
    }
    var r = this.abs();
    var sign = this.im >= 0 ? 1 : -1;
    return new Complex(Math.sqrt((r + this.re) / 2),
                       sign * Math.sqrt((r - this.re) / 2));
  };

  Complex.prototype.isZero = function (eps) {
    eps = eps == null ? 1e-10 : eps;
    return Math.abs(this.re) < eps && Math.abs(this.im) < eps;
  };
  Complex.prototype.isReal = function (eps) {
    eps = eps == null ? 1e-10 : eps;
    return Math.abs(this.im) < eps;
  };
  Complex.prototype.equals = function (b, eps) {
    b = Complex.from(b);
    eps = eps == null ? 1e-10 : eps;
    return Math.abs(this.re - b.re) < eps && Math.abs(this.im - b.im) < eps;
  };

  Complex.prototype.toString = function (decimals) {
    decimals = decimals == null ? 4 : decimals;
    var re = +this.re.toFixed(decimals);
    var im = +this.im.toFixed(decimals);
    var out = '';
    if (Math.abs(re) > 1e-10) out += re;
    if (Math.abs(im) > 1e-10) {
      if (im > 0 && out.length) out += '+';
      if (Math.abs(im - 1) < 1e-10) out += 'i';
      else if (Math.abs(im + 1) < 1e-10) out += '-i';
      else out += im + 'i';
    }
    return out.length ? out : '0';
  };

  Complex.prototype.toLaTeX = function (decimals, mode) {
    decimals = decimals == null ? 3 : decimals;
    mode = mode || 'decimal';
    var reZero = Math.abs(this.re) < 1e-10;
    var imZero = Math.abs(this.im) < 1e-10;
    if (reZero && imZero) return '0';

    if (mode === 'fraction') {
      var re = reZero ? null : toFraction(this.re);
      var im = imZero ? null : toFraction(this.im);
      if (re && im) {
        var imStr = formatImaginaryFraction(im);
        var sign = imStr[0] === '-' ? '' : '+';
        return re + sign + imStr;
      }
      if (re) return re;
      if (im) return formatImaginaryFraction(im);
      return '0';
    }

    var reS = reZero ? null : trimTrailingZeros(this.re.toFixed(decimals));
    var imS = imZero ? null : trimTrailingZeros(this.im.toFixed(decimals));
    if (reS === '-0') reS = '0';
    if (imS === '-0') imS = '0';
    if (reS && imS) {
      var imVal = parseFloat(imS);
      var sgn = this.im >= 0 ? '+' : '';
      var imStr2;
      if (Math.abs(imVal - 1) < 1e-10) imStr2 = 'i';
      else if (Math.abs(imVal + 1) < 1e-10) imStr2 = '-i';
      else imStr2 = imS + 'i';
      return reS + sgn + imStr2;
    }
    if (reS) return reS;
    if (imS) {
      var v = parseFloat(imS);
      if (Math.abs(v - 1) < 1e-10) return 'i';
      if (Math.abs(v + 1) < 1e-10) return '-i';
      return imS + 'i';
    }
    return '0';
  };

  function parseComplex(str) { return Complex.parse(str); }

  function toLatexComplex(z, decimals, mode) {
    if (z instanceof Complex) return z.toLaTeX(decimals, mode);
    if (typeof z === 'number') return new Complex(z, 0).toLaTeX(decimals, mode);
    if (z && typeof z === 'object' && 're' in z && 'im' in z) {
      return new Complex(z.re, z.im).toLaTeX(decimals, mode);
    }
    return String(z);
  }

  function isZeroLike(x, eps) {
    eps = eps == null ? 1e-10 : eps;
    if (x instanceof Complex) return x.isZero(eps);
    if (typeof x === 'number') return Math.abs(x) < eps;
    if (x && typeof x === 'object' && 're' in x && 'im' in x) {
      return Math.abs(x.re) < eps && Math.abs(x.im) < eps;
    }
    return false;
  }

  root.Complex = Complex;
  root.parseFraction = root.parseFraction || parseFraction;
  root.parseComplex = parseComplex;
  root.toFraction = root.toFraction || toFraction;
  root.toLatexComplex = toLatexComplex;
  root.isZeroLike = isZeroLike;
  root.formatImaginaryFraction = formatImaginaryFraction;
  root.trimTrailingZeros = trimTrailingZeros;
})(typeof window !== 'undefined' ? window : this);
