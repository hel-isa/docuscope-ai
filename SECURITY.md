# Security Policy

## Supported Versions

DocuScope AI is currently in active development and does not yet publish stable releases.

Security fixes are applied on a best-effort basis to the default branch.

| Version | Supported |
| ------- | --------- |
| `main`  | ✅ |
| Older commits / forks | ❌ |

## Reporting a Vulnerability

Please **do not report security vulnerabilities through public GitHub issues**.

Instead, please report them privately using one of these methods:

- **GitHub Security Advisories / Private vulnerability reporting** (preferred, if enabled)
- **Email:** `security@yourdomain.com`

If private reporting is not yet configured, please set it up in the repository’s **Security** tab and use that as the main reporting channel.

When submitting a report, please include:

- A clear description of the issue
- Affected component(s) or file(s)
- Steps to reproduce
- Proof of concept, sample payload, or screenshots if safe to share
- The potential impact
- Any suggested fix or mitigation

## What to Report

This repository processes documents and extracted text, so security reports are especially welcome for issues involving:

- Unauthorized access to uploaded or scanned documents
- Exposure of sensitive data in logs, exports, or intermediate files
- Broken masking / redaction of PII or confidential content
- Insecure file parsing or upload handling
- Path traversal
- Arbitrary file read/write
- Remote code execution
- Injection vulnerabilities
- Authentication or authorization flaws
- Dependency or supply-chain issues with practical impact
- Secrets committed to the repository
- AI / prompt-injection cases that cause unauthorized data disclosure
- OCR or document-processing flows that expose raw private content unexpectedly

## Out of Scope

The following are generally out of scope unless they create a clear, demonstrable security impact:

- Typographical or documentation errors
- Feature requests
- Theoretical issues without a realistic exploit path
- Denial-of-service requiring unrealistic resources
- Vulnerabilities only affecting unsupported code versions
- Problems in third-party services outside this repository’s control

## Response Process

We aim to:

- Acknowledge reports within **3 business days**
- Triage and validate the issue
- Keep the reporter informed during investigation
- Develop a fix or mitigation when appropriate
- Disclose details publicly only after remediation or coordinated disclosure

## Secure Development Expectations

Contributors should:

- Never commit secrets, API keys, tokens, or credentials
- Use `.env` files locally and keep real secrets out of version control
- Validate and sanitize all file inputs
- Treat uploaded files and extracted text as potentially sensitive
- Avoid logging raw confidential document contents
- Keep dependencies updated
- Review exports to ensure no sensitive data is unintentionally preserved
- Apply least privilege to any storage, API, or model integrations

## AI and Document Handling Notes

Because DocuScope AI analyzes documents and may use hybrid or AI-assisted classification:

- Model output must not be treated as inherently trustworthy
- Sensitive content should be masked before storage or export whenever possible
- Prompt injection and malicious document content should be considered in testing
- Sanitized outputs should be verified to ensure redaction actually occurred
- Debugging and error traces should not reveal private document contents

## Disclosure Policy

We follow coordinated disclosure:

1. Private report received
2. Vulnerability validated
3. Fix or mitigation prepared
4. Patch released to supported code
5. Public advisory shared when appropriate

## Additional Recommendations

For this repository, it is strongly recommended to enable:

- **Private vulnerability reporting** through GitHub Security
- **Dependabot alerts and updates** for Python dependencies
- **Secret scanning** and push protection
- **Code scanning** where available

GitHub documents SECURITY.md reporting guidance, and GitHub also provides security features such as dependency alerts, Dependabot, secret protection, and code scanning for supported repositories and plans. :contentReference[oaicite:2]{index=2}
