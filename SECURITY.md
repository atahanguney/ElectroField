# Security Policy & Technical Architecture

## 1. Overview and Scope

**ElectroField** is a client-side scientific computing and visualization workbench developed for multi-dimensional ($1\text{D}$–$4\text{D}$) electromagnetic field analysis and Maxwell equation solving. The software operates across two primary runtime environments:
1. **Browser-Based WebGL Runtime (`index.html`):** Executes entirely within the user's local browser sandbox using `Three.js` (WebGL 2.0) and HTML5 Canvas APIs.
2. **Standalone Desktop Distribution (`ElectroField.exe` / `.py`):** A local Python wrapper (`NumPy` / `Matplotlib` / `PyWebView`) compiled via `PyInstaller`.

Because the project processes user-defined mathematical expressions and parses external JSON payloads from an optional language model interface, this document outlines the security model, input validation mechanisms, and vulnerability reporting procedures for the repository.

---

## 2. Supported Versions

Security patches, parser rules, and dependency updates are maintained for the current stable branch (`main`) and the corresponding standalone executable release.

| Version | Distribution Target | Runtime Stack | Support Status |
| :--- | :--- | :--- | :--- |
| **2.5.x** | WebGL Workbench & Desktop `.exe` | `Three.js r128` / `Python 3.10+` | :white_check_mark: Active |
| **2.4.x** | Core WebGL Solver | `Three.js r128` | :warning: Maintenance Only |
| **< 2.4** | Early Academic Prototypes | Legacy DOM / Canvas | :x: Unsupported |

---

## 3. Technical Security Controls & Threat Model

### 3.1. Mathematical Expression Parser (`compileEquation`)
The workbench allows users to input custom parametric surface functions $Z(x, y, t)$ that are evaluated over a $48 \times 48$ vertex mesh ($2,401$ nodes) per animation frame.
* **Risk:** Dynamic code evaluation in JavaScript (`new Function` or `eval`) introduces arbitrary code execution (ACE) risks if raw strings are passed directly from the DOM.
* **Mitigation:** Prior to function compilation, `compileEquation(eqStr)` enforces a two-stage lexical filter:
  1. **Character Set Restriction:** The input string is tested against the regular expression `/^[A-Za-z0-9_$\s.+*\/%(),-]+$/`. Semicolons, brackets, assignment operators (`=`), and property accessors beyond standard dot notation are rejected.
  2. **Identifier Allowlisting:** All extracted identifier tokens (`/([A-Za-z_$][A-Za-z0-9_$]*)/g`) are checked against a static `Set` containing only spatial/temporal state variables (`x`, `y`, `r`, `t`, `freq`, `amp`, `sigma`, `epsR`, `muR`) and standard `Math` methods (`sin`, `cos`, `tan`, `exp`, `sqrt`, `pow`, `PI`, etc.). Any unrecognized token aborts compilation and reverts the solver to the default harmonic equation.

### 3.2. Cross-Site Scripting (XSS) & AI Payload Sanitization
The *AI Model Architect* module sends natural-language physics prompts to an external inference endpoint (`text.pollinations.ai`) and expects a structured JSON response containing simulation parameters.
* **Risk:** Untrusted external API responses or reflected user prompts could contain malformed HTML or inline `<script>` tags.
* **Mitigation:**
  * All user inputs and external text explanations are passed through `escapeHTML()`, which encodes `&`, `<`, `>`, `"`, and `'` into their respective HTML entities before DOM insertion.
  * Numeric parameters (`freq`, `epsR`, `muR`, `amp`, `sigma`) are coerced via `parseFloat()` and bounded by the range constraints of the simulation state.
  * The synthesized `customEq` field from the JSON response is routed through the same `compileEquation()` lexical allowlist described in Section 3.1.

### 3.3. WebGL Context & Main-Thread Resource Limits
* **Risk:** Unbounded geometry subdivisions or high-frequency `requestAnimationFrame` loops can cause GPU context loss (`webglcontextlost`) or main-thread starvation.
* **Mitigation:** Mesh resolution is fixed at `GRID_SEGMENTS = 48` and particle count is capped at `PARTICLE_COUNT = 350`. Viewport dimensions (`getBoundingClientRect`) are cached and updated only on window `resize` events to prevent forced synchronous layout reflows.

### 3.4. Standalone Desktop Binary (`ElectroField.exe`)
* The desktop executable is built from `build_desktop_exe.py` using `PyInstaller` in `--onefile` mode.
* It loads the local `index.html` asset via the `file://` URI scheme (`sys._MEIPASS`) inside an isolated `pywebview` or Chromium `--app` window without opening local network sockets or requiring administrative privileges.

---

## 4. Out of Scope

The following items are known architectural characteristics of a static GitHub Pages deployment and are considered out of scope for vulnerability reports:
* **HTTP Response Headers on GitHub Pages:** Static hosting on `github.io` does not support custom server-side HTTP headers such as strict `Content-Security-Policy` (CSP), `X-Frame-Options`, or `Cross-Origin-Opener-Policy` (COOP).
* **Client-Side Parameter Tampering:** Modifying `simState` variables locally via browser DevTools affects only the local client session; no server-side state or database exists.
* **Third-Party CDN Availability:** Availability or upstream integrity of public CDNs (`cdnjs.cloudflare.com`, `cdn.tailwindcss.com`, `fonts.googleapis.com`).

---

## 5. Reporting a Vulnerability

If a bypass in the `compileEquation()` lexical filter, a DOM-based XSS vector, or a packaging issue in the Python distribution is identified, please report it through one of the following channels rather than opening a public issue:

1. **GitHub Security Advisories:** Submit a report via the [**Security > Report a vulnerability**](https://github.com/atahanguney/ElectroField/security) tab in this repository.
2. **Direct Contact:** Reach out to the maintainer via GitHub or LinkedIn:
   * **Maintainer:** Atahan Güney (Department of Electrical & Electronics Engineering, Antalya Bilim University)
   * **GitHub:** [github.com/atahanguney](https://github.com/atahanguney)
   * **LinkedIn:** [linkedin.com/in/atahan-guney](https://www.linkedin.com/in/atahan-guney)

### What to Include in a Report
* A minimal proof-of-concept (PoC) input string or payload (e.g., the specific equation string that bypasses `allowedNames` in `compileEquation`).
* The target environment (Browser version / OS or Desktop `.exe` version).
* Expected behavior versus observed behavior.
