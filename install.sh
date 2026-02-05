#!/bin/bash
# Installation script for PII detection pre-commit hook

set -e

echo "🔧 Setting up PII detection pre-commit hook..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "Error: pip is required but not installed."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt || pip install -r requirements.txt

# Download spaCy model
echo "📥 Downloading spaCy language model..."
if ! python3 -m spacy download en_core_web_sm; then
    echo "Error: Failed to download spaCy model."
    echo "Please try again or manually run: python3 -m spacy download en_core_web_sm"
    exit 1
fi

# Copy pre-commit hook to .git/hooks
echo "🔗 Installing pre-commit hook..."
mkdir -p .git/hooks
cp hooks/pre-commit-pii.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "✅ PII detection pre-commit hook installed successfully!"
echo ""
echo "The hook will now run automatically on every commit."
echo "To bypass the hook, use: git commit --no-verify"
