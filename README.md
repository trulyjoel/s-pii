# s-pii

A pre-commit git hook that detects Personally Identifiable Information (PII) in your commits using Microsoft Presidio.

## Features

- 🔍 **Automatic PII Detection**: Scans staged files before commit
- 📊 **Detailed Reporting**: Shows count of each PII type found
- 📍 **Location Information**: Displays exact file, line, and column where PII was detected
- 🎯 **Context Display**: Shows the line containing PII for easy identification
- ⚡ **Fast Analysis**: Leverages Microsoft Presidio's AI-powered detection

## Detected PII Types

The hook can detect various types of PII including:
- Email addresses
- Phone numbers
- Credit card numbers
- Social Security Numbers (SSN)
- IP addresses
- Person names
- Medical license numbers
- And more...

## Installation

### Prerequisites

- Python 3.7 or higher
- pip
- git

### Quick Install

Run the installation script:

```bash
./install.sh
```

This will:
1. Install Python dependencies (presidio-analyzer, presidio-anonymizer)
2. Download the required spaCy language model
3. Set up the pre-commit hook in your `.git/hooks` directory

### Manual Installation

If you prefer manual installation:

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Copy hook to .git/hooks
cp hooks/pre-commit-pii.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Usage

Once installed, the hook runs automatically on every `git commit`. 

### Normal Workflow

```bash
# Stage your changes
git add .

# Commit (hook runs automatically)
git commit -m "Your commit message"
```

### If PII is Detected

When PII is found, the hook will:
1. Block the commit
2. Display a summary of PII types and counts
3. Show exact locations where PII was found
4. Provide context for each detection

Example output:
```
⚠️  WARNING: PII detected in your commit!

📊 PII Summary:
------------------------------------------------------------
  EMAIL_ADDRESS: 2
  PHONE_NUMBER: 1
  PERSON: 3
------------------------------------------------------------
  Total PII instances: 6
  Files affected: 2

📍 PII Locations:
------------------------------------------------------------
  example.py:15:23 - EMAIL_ADDRESS (score: 0.95)
    Found: 'user@example.com'
    Context: email = "user@example.com"

  data.txt:5:1 - PHONE_NUMBER (score: 0.75)
    Found: '555-123-4567'
    Context: Phone: 555-123-4567
------------------------------------------------------------

⛔ Commit blocked due to PII detection.
Please review and remove PII before committing.
If this is intentional, you can bypass with: git commit --no-verify
```

### Bypassing the Hook

If you intentionally need to commit PII (e.g., test data, documentation):

```bash
git commit --no-verify -m "Your commit message"
```

**⚠️ Warning**: Use `--no-verify` with caution and ensure you understand the implications.

## Configuration

### Skipped Files

The hook automatically skips:
- Binary files (images, PDFs, executables)
- Dependencies directories (node_modules, venv, etc.)
- Build artifacts (dist, build, etc.)

To customize, edit the `should_skip_file()` function in `hooks/pre-commit-pii.py`.

### PII Entity Types

By default, all Presidio entity types are analyzed. To customize which PII types to detect, modify the `entities` parameter in the `analyze_text_for_pii()` function.

## Using with pre-commit Framework

This repository includes a `.pre-commit-config.yaml` file for use with the [pre-commit](https://pre-commit.com/) framework:

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install

# Run on all files (optional)
pre-commit run --all-files
```

## How It Works

1. **Staged File Detection**: The hook identifies all files staged for commit
2. **Content Extraction**: Retrieves the staged content of each file
3. **PII Analysis**: Uses Microsoft Presidio's analyzer to scan for PII
4. **Result Formatting**: Organizes findings by type and location
5. **User Alert**: Displays detailed report and blocks commit if PII is found

## Troubleshooting

### "presidio-analyzer is not installed"

Run: `pip install -r requirements.txt`

### "spaCy model not found"

Run: `python -m spacy download en_core_web_sm`

### Hook not running

Ensure the hook is executable:
```bash
chmod +x .git/hooks/pre-commit
```

### False positives

Presidio may occasionally flag non-PII data. Review each detection and use `--no-verify` if needed.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT

## Acknowledgments

- [Microsoft Presidio](https://github.com/microsoft/presidio) - PII detection and anonymization
- [spaCy](https://spacy.io/) - NLP processing