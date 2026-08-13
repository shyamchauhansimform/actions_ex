# Security CI/CD Pipeline — Demo Project

An intentionally vulnerable demo application used to showcase a comprehensive **DevSecOps pipeline** with 10 automated security tools integrated via GitHub Actions.

> ⚠️ **This project contains intentional vulnerabilities for demonstration purposes. Do NOT deploy to production.**

---

## Project Structure

```
.
├── app.py                  # Intentional code smells & vulnerabilities (SonarCloud demo)
├── vuln_app.py             # Intentionally vulnerable Flask app (DAST target)
├── main.py                 # Hardcoded secrets (secret scanning demo)
├── requirements.txt        # Outdated Python dependencies (SCA demo)
├── package.json            # JS dependencies (Retire.js demo)
├── nuclei-templates/       # Custom Nuclei scan templates
└── .github/workflows/      # All CI/CD security pipelines
```

---

## Security Workflows

### SAST — Static Application Security Testing

| Tool | File | Purpose |
|------|------|---------|
| [SonarCloud](https://sonarcloud.io) | `sonarcloud.yml` | Code quality, bugs, code smells, and security hotspots |

---

### DAST — Dynamic Application Security Testing

| Tool | File | Purpose |
|------|------|---------|
| [Wapiti](https://wapiti-scanner.github.io) | `wapiti.yml` | Black-box web vulnerability scanning (SQLi, XSS, open redirects, etc.) |
| [Nuclei](https://nuclei.projectdiscovery.io) | `nuclei.yml` | Template-based vulnerability scanning using custom templates in `nuclei-templates/` |

---

### SCA — Software Composition Analysis

| Tool | File | Purpose |
|------|------|---------|
| [Snyk](https://snyk.io) | `snyk.yml` | Dependency vulnerability scan for Python packages + SARIF upload |
| [CVE Lite CLI](https://github.com/OWASP/cve-lite-cli) | `cve-lite-cli.yml` | OWASP CVE lookup for dependencies |
| [Retire.js](https://retirejs.github.io/retire.js/) | `retirejs.yml` | Detects JS libraries with known CVEs |

---

### Secret Scanning

| Tool | File | Purpose |
|------|------|---------|
| [Gitleaks](https://github.com/gitleaks/gitleaks) | `gitleaks.yml` | Detects hardcoded secrets and credentials in code |
| [TruffleHog](https://github.com/trufflesecurity/trufflehog) | `trufflehog.yml` | Deep secret scanning across full git history |

---

### Supply Chain Security

| Tool | File | Purpose |
|------|------|---------|
| [Chain Bench](https://github.com/aquasecurity/chain-bench) | `chain-bench.yml` | CIS Software Supply Chain Benchmark audit of the GitHub org/repo |
| [cdxgen](https://github.com/CycloneDX/cdxgen) | `cdxgen-sbom.yml` | Generates a CycloneDX SBOM (Software Bill of Materials) |
| [SLSA](https://github.com/slsa-framework/slsa) | `slsa.yml` | SLSA Build Level 3 provenance attestation for build artifacts |

---

## Intentional Vulnerabilities (Demo Targets)

| File | Vulnerability Type | Detected By |
|------|--------------------|-------------|
| `main.py` | Hardcoded API key, AWS access key | TruffleHog, Gitleaks |
| `vuln_app.py` | SQLi, XSS, open redirect, command injection, insecure cookie | Wapiti, Nuclei |
| `app.py` | Command injection, code smells, cognitive complexity, null returns | SonarCloud |
| `requirements.txt` | Outdated packages with known CVEs | Snyk, CVE Lite CLI |
| `package.json` | Outdated JS devDependencies | Retire.js |

---

## Required Secrets

Configure these in **Settings → Secrets and variables → Actions**:

| Secret | Required By |
|--------|-------------|
| `SONAR_TOKEN` | SonarCloud |
| `SNYK_TOKEN` | Snyk |
| `CHAIN_BENCH_TOKEN` | Chain Bench (PAT with `repo`, `read:org`, `admin:org_hook` scopes) |

---

## Pipeline Overview

```
Push / PR
    │
    ├── SonarCloud          (SAST — code quality & security)
    ├── Gitleaks            (secret scan — git history delta)
    ├── TruffleHog          (secret scan — full history on push; PR diff on PR)
    ├── Snyk                (SCA — Python CVEs + SARIF)
    ├── CVE Lite CLI        (SCA — OWASP CVE lookup)
    ├── Retire.js           (SCA — JS library CVEs)
    ├── cdxgen              (SBOM — CycloneDX)
    ├── Chain Bench         (supply chain — CIS benchmark)
    ├── SLSA                (supply chain — SLSA Build L3 provenance)
    ├── Wapiti              (DAST — black-box web scan)
    └── Nuclei              (DAST — template-based scan)
```
