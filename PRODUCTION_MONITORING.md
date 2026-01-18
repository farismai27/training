# Production Monitoring & Auto-Fix

Automatic error detection and fixing for your MCP server - Claude monitors production, finds bugs, and creates PRs with fixes while you sleep! 🌙

## 🎯 What This Does

Your project now has **automated production monitoring** that:

✅ **Runs daily at 6 AM UTC** (automated schedule)
✅ **Fetches production logs** (tests, errors, code issues)
✅ **Analyzes errors with Claude** (AI-powered debugging)
✅ **Generates fixes automatically** (code changes)
✅ **Creates Pull Requests** (ready for review)
✅ **You wake up to fixed bugs!** ☕

## 📊 The Workflow

```
6:00 AM UTC: GitHub Action triggers
    ↓
Fetch last 24 hours of logs
    ↓
Run tests → Capture failures
    ↓
Scan code → Find TODO/FIXME/BUG markers
    ↓
Claude analyzes each error
    ↓
Claude generates fixes
    ↓
Apply fixes to codebase
    ↓
Commit changes
    ↓
Create Pull Request
    ↓
8:00 AM: You wake up → Review PR → Merge!
```

## 🚀 Quick Start

### 1. Set Up GitHub Secret

Add your Anthropic API key to GitHub Secrets:

1. Go to your repo: https://github.com/farismai27/training
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`
5. Value: Your API key from https://console.anthropic.com/
6. Click **Add secret**

### 2. Enable GitHub Actions

The workflow is already in your repository at `.github/workflows/auto-fix-errors.yml`

It will run automatically:
- **Daily at 6 AM UTC**
- **Or manually** when you trigger it

### 3. Manual Trigger (Test It Now!)

1. Go to **Actions** tab on GitHub
2. Click **Auto-Fix Production Errors**
3. Click **Run workflow**
4. Choose options:
   - Hours of logs: `24` (default)
   - Max errors: `5` (default)
5. Click **Run workflow**

Wait 2-3 minutes, then check for a new Pull Request!

## 📁 File Structure

```
training/
├── .github/
│   └── workflows/
│       └── auto-fix-errors.yml      # GitHub Action workflow
├── scripts/
│   └── auto_fix_errors.py           # Error analysis script
├── src/
│   ├── logging_config.py            # Structured logging
│   └── document_server.py           # Updated with logging
└── logs/                            # Log files (gitignored)
    ├── document_server.log          # Server logs
    ├── test_errors.log              # Test failures
    ├── code_issues.log              # TODO/FIXME markers
    └── summary.txt                  # Fix summary
```

## 🔧 How It Works

### Step 1: Log Collection

The workflow collects errors from multiple sources:

#### A. **Test Failures**
```bash
pytest tests/ -v --tb=short
```
Captures:
- Failed test names
- Assertion errors
- Exception tracebacks

#### B. **Code Issues**
```bash
grep -r "TODO\|FIXME\|BUG\|HACK" src/ tests/
```
Finds:
- TODO comments needing attention
- FIXME markers
- Known bugs
- Code hacks

#### C. **Git History**
```bash
git log --since="24 hours ago"
```
Searches recent commits for:
- Error messages
- Exception reports
- Failed deployments

### Step 2: Error Analysis

Claude analyzes each error and provides:
- **Root cause analysis**
- **Specific fix with file paths**
- **Code changes needed**
- **Explanation of why**

Example analysis:
```json
{
  "analysis": "Invalid model ID in production config",
  "files_to_modify": [{
    "path": "src/config.py",
    "changes": "Update ANTHROPIC_MODEL from invalid ID to correct one",
    "code": "ANTHROPIC_MODEL = 'claude-sonnet-4-20250514'"
  }],
  "explanation": "The model ID typo causes API failures in production"
}
```

### Step 3: Fix Application

The script applies fixes to your codebase:
- Modifies the specified files
- Adds explanatory comments
- Preserves code structure
- Creates commit with changes

### Step 4: Pull Request

Creates a PR with:
- **Title**: "🤖 Auto-fix: Production Errors (#123)"
- **Summary**: List of errors fixed
- **Changes**: Detailed code modifications
- **Labels**: `automated`, `bug-fix`, `needs-review`
- **Checklist**: Review steps

## 💡 Example: Real Error Fix

### The Error
```
FAILED tests/test_document_conversion.py::test_valid_pdf_conversion
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/test.pdf'
```

### Claude's Analysis
```
Root Cause: Test expects PDF file at /tmp/test.pdf but file doesn't exist

Fix: Update test to use existing PDF from data/ directory or create test fixture

Files to Modify:
- tests/test_document_conversion.py
  Change: Use existing PDF file from data/ directory
  Code: pdf_path = "data/OneSuite-Platform User Stories.pdf"
```

### The PR
```markdown
## 🤖 Automated Error Fixes

### Fix 1: Test PDF File Not Found
**Root Cause:** Test references non-existent PDF file
**Fix:** Updated test to use existing PDF from data/ directory
**File:** tests/test_document_conversion.py

### Review Checklist
- [ ] Verify fix is correct
- [ ] Run tests locally
- [ ] Merge if approved
```

## ⚙️ Configuration

### Adjust Schedule

Edit `.github/workflows/auto-fix-errors.yml`:

```yaml
schedule:
  - cron: '0 6 * * *'  # 6 AM UTC daily

# Change to:
  - cron: '0 */6 * * *'  # Every 6 hours
  - cron: '0 9 * * 1-5'  # 9 AM weekdays only
  - cron: '0 0 * * *'    # Midnight daily
```

### Change Error Limit

```yaml
env:
  MAX_ERRORS: 5  # Change to 10, 20, etc.
```

### Add CloudWatch Integration

If you deploy to AWS, add CloudWatch log fetching:

```yaml
- name: Fetch CloudWatch Logs
  run: |
    aws logs tail /aws/lambda/mcp-server \
      --since 24h \
      --format short \
      > logs/cloudwatch.log
```

### Add Heroku Integration

For Heroku apps:

```yaml
- name: Fetch Heroku Logs
  run: |
    heroku logs --app your-app-name \
      --num 1000 \
      > logs/heroku.log
```

## 📊 Monitoring Dashboard

View your auto-fix activity:

1. **Actions Tab**: See workflow runs
2. **Pull Requests**: Review auto-generated PRs
3. **Artifacts**: Download detailed logs (kept for 7 days)

## 🎯 Best Practices

### 1. Review Before Merging
Always review auto-generated PRs:
- Check the analysis is correct
- Verify the fix makes sense
- Run tests locally if unsure

### 2. Add Tests
After merging a fix, add tests:
- Prevent regression
- Validate the fix works
- Improve coverage

### 3. Monitor Patterns
If you see recurring errors:
- May indicate deeper issues
- Consider architectural changes
- Add more comprehensive fixes

### 4. Keep API Key Secure
- Never commit API keys
- Use GitHub Secrets only
- Rotate keys periodically

### 5. Limit Error Count
Start with MAX_ERRORS=5:
- Prevents overwhelming PRs
- Keeps fixes focused
- Easier to review

## 🔍 Troubleshooting

### No PR Created

**Check:**
- Workflow ran successfully (Actions tab)
- Errors were found in logs
- Claude generated fixes
- Changes were committed

**View logs:**
```bash
# In Actions tab, click the run
# Expand each step to see detailed output
```

### API Key Issues

**Error:** "ANTHROPIC_API_KEY not set"

**Solution:**
1. Verify secret is created in GitHub Settings
2. Name must be exactly `ANTHROPIC_API_KEY`
3. Check API key is valid at https://console.anthropic.com/

### Workflow Not Running

**Check:**
- Workflows are enabled (Settings → Actions)
- Cron schedule is correct (UTC timezone)
- Manual trigger works (Run workflow button)

### Too Many Errors

**Solution:**
1. Reduce MAX_ERRORS in workflow
2. Fix high-priority errors first
3. Run multiple times to fix incrementally

## 📈 Metrics & Analytics

Track your auto-fix performance:

### Workflow Runs
- **Total runs**: Actions → Auto-Fix Production Errors
- **Success rate**: Green ✓ vs Red ✗
- **Average duration**: Check workflow times

### PRs Created
- **Auto-fix PRs**: Filter by `automated` label
- **Merge rate**: How many you merge
- **Time to merge**: How quickly you review

### Errors Fixed
- **Daily**: Check summary.txt in artifacts
- **Weekly**: Sum up all runs
- **Most common**: Pattern analysis

## 🚀 Advanced Features

### Custom Error Sources

Add your own log sources in the workflow:

```yaml
- name: Fetch Custom Logs
  run: |
    # Your custom logging system
    curl https://api.yourapp.com/logs \
      > logs/custom.log
```

### Slack Notifications

Get notified when PRs are created:

```yaml
- name: Notify Slack
  if: steps.check_changes.outputs.has_changes == 'true'
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
      -d '{"text":"🤖 Auto-fix PR created!"}'
```

### Email Reports

Send daily summaries:

```yaml
- name: Email Report
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{secrets.MAIL_USERNAME}}
    password: ${{secrets.MAIL_PASSWORD}}
    subject: Daily Auto-Fix Report
    body: file://logs/summary.txt
```

## 🎓 Learning from Auto-Fixes

Use auto-fixes as learning opportunities:

### Patterns
- **Common mistakes**: What errors recur?
- **Code smells**: What needs refactoring?
- **Test gaps**: What's not covered?

### Improvements
- **Add guards**: Prevent future errors
- **Improve docs**: Clarify confusing areas
- **Refactor**: Address root causes

### Team Knowledge
- **Share fixes**: Discuss in code reviews
- **Document**: Update docs based on fixes
- **Train**: Learn from Claude's analysis

## 🎉 Success Stories

### Example 1: Missing File Check
**Before:** Tests fail randomly when PDF missing
**Auto-Fix:** Added file existence check
**Result:** Tests always pass ✅

### Example 2: Type Mismatch
**Before:** Production errors with wrong types
**Auto-Fix:** Added proper type hints and validation
**Result:** Type errors caught early ✅

### Example 3: Configuration Bug
**Before:** Production uses wrong API model
**Auto-Fix:** Corrected model ID in config
**Result:** API calls work in production ✅

## 📚 Resources

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Anthropic API**: https://docs.anthropic.com
- **Claude Code**: https://claude.ai/code
- **Python Logging**: https://docs.python.org/3/library/logging.html

## 🎯 Next Steps

1. ✅ Set up ANTHROPIC_API_KEY in GitHub Secrets
2. ✅ Test the workflow manually (Run workflow button)
3. ✅ Review the auto-generated PR
4. ✅ Merge your first auto-fix!
5. ✅ Enable daily schedule
6. ✅ Wake up to fixed bugs every morning! ☕

---

**Welcome to the future of production monitoring!** 🚀

Your code now has a 24/7 AI engineer watching for errors and fixing them automatically.

**Sleep well knowing Claude is on duty!** 🌙

---

*This monitoring system is powered by Claude Sonnet 4 and GitHub Actions.*
*Customize it to fit your specific needs and deployment environment.*
