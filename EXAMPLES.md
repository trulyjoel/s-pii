# Example Files for Testing PII Detection

This directory contains sample files to test the PII detection hook.

## Test Files

### test_pii.txt
Contains various types of PII including:
- Email addresses
- Phone numbers
- Social Security Numbers
- Names
- Credit card numbers
- IP addresses

This file should trigger the pre-commit hook and block the commit.

### test_clean.txt
Contains no PII and should pass the pre-commit hook check.

## Testing the Hook

1. **Test with PII file:**
   ```bash
   git add test_pii.txt
   git commit -m "Test with PII"
   # Should be blocked with detailed PII report
   ```

2. **Test with clean file:**
   ```bash
   git add test_clean.txt
   git commit -m "Test without PII"
   # Should pass successfully
   ```

3. **Bypass the hook (if needed):**
   ```bash
   git commit --no-verify -m "Bypass PII check"
   # Commits without running the hook
   ```

## Expected Output

When PII is detected, you'll see:
- A summary count of each PII type
- Exact file locations (file:line:column)
- The actual PII text found
- Context showing the line containing PII
- Exit code 1 (blocking the commit)

When no PII is detected:
- A success message
- Exit code 0 (allowing the commit)
