# Contributing to DocuScope AI

Thank you for your interest in contributing to DocuScope AI! We appreciate your help making this project better.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Before You Start](#before-you-start)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Security & Privacy](#security--privacy)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Getting Help](#getting-help)

---

## Code of Conduct

We are committed to providing a welcoming and respectful environment for all contributors.

- Be respectful and inclusive
- Give credit where due
- Report issues responsibly
- Focus on the code, not the person

---

## Before You Start

Please review these resources before contributing:

1. **[Security Policy](SECURITY.md)** - Important security guidelines
2. **[Privacy Model](README.md#privacy-model)** - How we handle sensitive data
3. **[Architecture](README.md#current-architecture)** - System design overview
4. **[Existing PRs](https://github.com/hel-isa/docuscope-ai/pulls)** - Avoid duplicate work

---

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- macOS, Linux, or Windows (with WSL2 recommended)

### 1. Fork & Clone the Repository

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/docuscope-ai.git
cd docuscope-ai
git remote add upstream https://github.com/hel-isa/docuscope-ai.git
```

### 2. Create Virtual Environment

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
python -m venv .venv
.venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest pytest-cov flake8 black mypy bandit
```

### 4. Install System Dependencies

#### macOS

```bash
brew install tesseract poppler
```

#### Ubuntu / Debian

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
```

#### Other Linux Distributions

Install `tesseract-ocr` and `poppler-utils` using your package manager.

### 5. Verify Setup

```bash
# Run tests
pytest tests/ -v

# Check version
python --version
tesseract --version
```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

**Branch naming convention:**
- `feature/description` - New features (e.g., `feature/enhanced-pii-detection`)
- `fix/description` - Bug fixes (e.g., `fix/ocr-rotation-handling`)
- `docs/description` - Documentation (e.g., `docs/api-guide`)
- `chore/description` - Maintenance (e.g., `chore/update-dependencies`)
- `refactor/description` - Code refactoring (e.g., `refactor/privacy-module`)
- `security/description` - Security fixes (e.g., `security/input-validation`)

### 2. Make Your Changes

```bash
# Edit files
# Add tests for new functionality
# Update documentation
```

### 3. Run Quality Checks Before Committing

```bash
# Format code with Black
black app tests

# Lint with flake8
flake8 app tests

# Type check with mypy
mypy app --ignore-missing-imports

# Security scan with Bandit
bandit -r app/ -ll

# Run tests
pytest tests/ -v --cov=app
```

### 4. Commit Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): subject line (50 chars max)

Detailed explanation if needed (wrap at 72 chars).

Closes #123
```

**Valid types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Formatting (not functional)
- `refactor:` - Code refactoring
- `perf:` - Performance improvement
- `test:` - Adding/updating tests
- `chore:` - Build/dependency updates
- `security:` - Security fixes

**Examples:**

```
feat(privacy): implement HMAC-SHA256 email masking

Adds more secure email masking using HMAC-SHA256 instead of 
simple pattern-based masking. Improves privacy for personally 
identifiable email addresses.

- Implement HMAC-based masking utility
- Add tests for reversibility guarantee
- Update masking documentation

Closes #42
```

```
fix(ocr): handle rotated images correctly

Fixes issue where OCR would fail on images rotated 90+ degrees.
Adds rotation detection and auto-correction.

Closes #38
```

### 5. Push Your Changes

```bash
git fetch upstream
git rebase upstream/main
git push origin feature/your-feature-name
```

---

## Code Standards

### Python Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with Black for formatting.

**Key rules:**
- 4 spaces for indentation
- Max line length: 100 characters (Black default)
- Use descriptive variable names
- Avoid `import *`
- Use type hints where practical

### Code Quality Targets

| Metric | Target |
|--------|--------|
| Test Coverage | 80%+ |
| Linting | No violations |
| Type Hints | 70%+ of functions |
| Complexity | Max 10 per function |

### Documentation

- Add docstrings to all functions/classes
- Update README for new features
- Document security implications
- Include examples for complex functionality

**Docstring format:**

```python
def mask_email(email: str, hash_algo: str = "sha256") -> str:
    """
    Mask email addresses for privacy protection.
    
    This function masks email addresses to prevent exposure of
    personal email data while maintaining consistent patterns
    for duplicate detection.
    
    Args:
        email: The email address to mask.
        hash_algo: Hash algorithm to use (default: sha256).
    
    Returns:
        Masked email in format MASKED-[hash].
    
    Raises:
        ValueError: If email format is invalid.
    
    Example:
        >>> mask_email("john@example.com")
        'MASKED-abc123...'
    
    Security Note:
        The masking is deterministic and reversible only with
        the original hash. Outputs are sanitized for logging.
    """
    # Implementation...
```

---

## Testing

### Writing Tests

Create tests in `tests/` directory matching the module being tested:

```
tests/
├── test_parsers.py          # tests for app/parsers/
├── test_privacy.py          # tests for app/privacy/
├── test_classify.py         # tests for app/classify/
└── test_export.py           # tests for app/export/
```

**Test template:**

```python
import pytest
from app.privacy import mask_email

class TestMaskEmail:
    """Test suite for email masking functionality."""
    
    def test_mask_email_basic(self):
        """Test basic email masking."""
        result = mask_email("john@example.com")
        assert result.startswith("MASKED-")
        assert "@" not in result
    
    def test_mask_email_preserves_consistency(self):
        """Test that same email always produces same mask."""
        email = "jane@example.com"
        result1 = mask_email(email)
        result2 = mask_email(email)
        assert result1 == result2
    
    def test_mask_email_invalid_format(self):
        """Test that invalid emails raise ValueError."""
        with pytest.raises(ValueError):
            mask_email("not-an-email")
    
    @pytest.mark.parametrize("email", [
        "simple@example.com",
        "with.dots@example.co.uk",
        "with+alias@example.com",
    ])
    def test_mask_email_various_formats(self, email):
        """Test masking various email formats."""
        result = mask_email(email)
        assert result.startswith("MASKED-")
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test
pytest tests/test_privacy.py::TestMaskEmail::test_mask_email_basic -v

# Run tests matching pattern
pytest tests/ -k "mask_email" -v
```

### Test Coverage

Aim for 80%+ coverage:

```bash
# Generate coverage report
pytest tests/ --cov=app --cov-report=html

# View in browser
open htmlcov/index.html
```

---

## Security & Privacy

### When Modifying Privacy Modules

✅ **DO:**
- Test masking with realistic data (without real sensitive data in repo)
- Verify no sensitive data leaks in logs
- Document regex/pattern changes
- Update security tests
- Think about edge cases and attacks

❌ **DON'T:**
- Commit real PII or sensitive data
- Log raw document contents
- Bypass masking for "temporary debugging"
- Trust user input without validation

### When Adding Dependencies

✅ **DO:**
- Check security advisories on [CVE Details](https://www.cvedetails.com/)
- Review maintenance status and community
- Document rationale in PR
- Pin versions in `requirements.txt`
- Use minimal dependencies

❌ **DON'T:**
- Add unmaintained packages
- Use packages with security issues
- Commit without documenting why
- Use versions with known vulnerabilities

### Commit Message Verification

Never commit:
- API keys or tokens
- Passwords or authentication credentials
- Database credentials
- Private keys or certificates
- Real PII or sensitive test data

**Pre-commit check:**
```bash
# Search your changes for suspicious patterns
git diff --cached | grep -i "password\|api_key\|secret\|token"
```

---

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Example Commits

**Feature:**
```
feat(privacy): add credit card masking

Implement LUHN algorithm-aware credit card masking that 
preserves last 4 digits for verification purposes.

- Add luhn_validator utility
- Implement CC masking in PII detector
- Add comprehensive test suite
- Update privacy documentation

Closes #145
```

**Bug Fix:**
```
fix(parser): handle corrupted PDF headers

Some PDFs have non-standard headers that cause PyPDF2 to fail.
Add fallback parser using pdfplumber for corrupted files.

Closes #139
```

**Documentation:**
```
docs(readme): add privacy model explanation

Add detailed section on how DocuScope AI handles sensitive data:
- When data is masked
- How masking works
- What data is exported
- Privacy guarantees

Addresses issue #100
```

---

## Pull Request Process

### Before Submitting

- [ ] Branch is up to date with `main`
- [ ] All tests pass locally
- [ ] Code follows PEP 8 / Black formatting
- [ ] No new security warnings
- [ ] Test coverage ≥ 80%
- [ ] Documentation updated
- [ ] No secrets or sensitive data committed

### Submitting

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open PR on GitHub**
   - Use the PR template
   - Describe changes clearly
   - Link related issues with `Closes #123`
   - Explain security/privacy implications

3. **Example PR Description**
   ```markdown
   ## Description
   Improves PII detection with machine learning confidence scoring.
   
   ## Type of Change
   - [x] New feature
   - [ ] Bug fix
   - [ ] Documentation
   
   ## Changes
   - Integrate spaCy NER for entity detection
   - Add confidence scoring to all PII detections
   - Improve false positive handling
   
   ## Testing
   - Added 15 new test cases
   - Coverage: 94%
   - All tests passing ✅
   
   ## Security Checklist
   - [x] No secrets committed
   - [x] No unmasked PII in outputs
   - [x] No new dependencies with known issues
   - [x] Code reviewed for injection risks
   
   ## Privacy Impact
   The change doesn't alter what data is masked, only how 
   confidently we detect it. Actual masking behavior unchanged.
   
   Closes #123
   ```

### Code Review

- **Response time:** 3-7 business days
- **Approval required:** Minimum 1
- **Status checks:** All must pass
- **Branch protection:** Up to date with main

### Addressing Feedback

1. Make requested changes in new commits
2. Don't force-push (preserves review history)
3. Request re-review when ready
4. Respond to all comments

### Merging

Once approved and all checks pass:
- Maintainer will merge with squash or rebase (depending on commit quality)
- Your feature branch can be deleted
- Close related issues

---

## Getting Help

### Questions?

- **Documentation:** Check [README](README.md) and [SECURITY.md](SECURITY.md)
- **Architecture:** See [Current Architecture](README.md#current-architecture)
- **Privacy Details:** Review [Privacy Model](README.md#privacy-model)

### Found an Issue?

1. Check [existing issues](https://github.com/hel-isa/docuscope-ai/issues)
2. If new, open a bug report using the template
3. For security issues, see [SECURITY.md](SECURITY.md)

### Have a Feature Idea?

1. Open a feature request using the template
2. Describe the use case and why it's needed
3. Discuss implementation approach
4. Wait for feedback before starting work

### Need Direct Help?

- Comment on related issues
- Check recent PRs for similar work
- Read the codebase comments and docstrings

---

## Tips for Successful Contributions

✅ **DO:**
- Start small (1-2 files rather than 10)
- Write tests first (TDD mindset)
- Ask before large refactors
- Reference issues when possible
- Give credit in commit messages
- Review your own code first

❌ **DON'T:**
- Mix unrelated changes in one PR
- Skip tests to "move faster"
- Refactor large sections without discussion
- Change formatting of unrelated code
- Commit with `--no-verify` to skip checks
- Give up if first review asks for changes!

---

## Attribution

Contributors will be recognized in:
- PR merge commit
- Project contributors list (upcoming)
- Release notes for new versions

---

## Thank You! 🙏

Your contributions make DocuScope AI better. Whether it's code, tests, documentation, or bug reports — we appreciate your help!

**Questions?** Open an issue or check [SECURITY.md](SECURITY.md) for security concerns.

**Happy coding!** 🚀
