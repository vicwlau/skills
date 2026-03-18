---
name: figma-handoff
description: Analyzes Figma design files and generates developer handoff documentation. Use when user uploads .fig files, asks for "design specs", "component documentation", or "design-to-code handoff"
---

# figma-handoff

## Instructions

### Step 1: Validate the Figma file
Run `python scripts/validate.py --input {filename}` to check data format. If validation fails, common issues include:
- Missing required fields (add them to the CSV)
- Invalid date formats (use YYYY-MM-DD)

## Common Issues

### MCP Connection Failed
If you see "Connection refused":
1. Verify MCP server is running: Check Settings > Extensions
2. Confirm API key is valid
3. Try reconnecting: Settings > Extensions > [Your Service] > Reconnect

## Configuration
Before writing queries, consult `references/api-patterns.md` for:
- Rate limiting guidance
- Pagination patterns
- Error codes and handling