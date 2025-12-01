# How to Run the Pipeline with Your Claude Code API Key

Since you're running in Claude Code, you already have an authenticated session, but the Python subprocess needs explicit access to your API key.

## Option 1: Set API Key for One Run (Recommended for Security)

```bash
# Set the API key just for this command (it won't be saved)
ANTHROPIC_API_KEY=your_api_key_here venv/bin/python3 main.py
```

## Option 2: Create .env File Locally (NOT committed to git)

The `.env` file is already in `.gitignore`, so it's safe to create locally:

```bash
# Edit the .env file
nano .env

# Add your API key:
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Save and run
venv/bin/python3 main.py
```

## Option 3: Export for Current Shell Session

```bash
# Export the key (valid for current terminal session only)
export ANTHROPIC_API_KEY=your_api_key_here

# Run the pipeline
venv/bin/python3 main.py
```

## Finding Your API Key

1. Go to https://console.anthropic.com/settings/keys
2. Copy your API key
3. Use one of the methods above

## Running Without Cross-Checking (Less API Usage)

If you want to reduce API costs, you can disable cross-checking:

```bash
#  Edit main.py and change:
output_file = creator.run(
    cross_check=False,  # Disable cross-checking
    enrich=False,       # Disable Wikipedia enrichment
    max_segments=5      # Process only 5 segments
)
```

This will significantly reduce API usage while still demonstrating the translation pipeline.

## Expected Costs

- **5 segments (testing)**: ~$1-2
- **Full book (~40 segments)**: ~$20-50
- **Without cross-checking**: ~50% less

## Security Note

Your API key will NEVER be committed to git because:
- `.env` is in `.gitignore`
- Environment variables are session-only
- The code uses automatic discovery when possible
