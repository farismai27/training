# Parallel Development with Git WorkTrees

A comprehensive guide to running multiple Claude Code instances in parallel using Git WorkTrees - enabling you to command your own team of virtual software engineers!

## 🎯 What This Enables

With this setup, you can:
- **Run 4+ Claude instances simultaneously** working on different features
- **Eliminate file conflicts** - each instance works in isolation
- **Merge automatically** - Claude handles merge conflicts for you
- **Scale your productivity** - work on multiple features at once
- **Maintain clean code** - each feature branch is independent

## 📁 How It Works

### Traditional Development (Sequential)
```
Main Branch
  ├── Feature A (work, commit, merge)
  ├── Feature B (work, commit, merge)  ← Wait for A
  └── Feature C (work, commit, merge)  ← Wait for B
```

### Parallel Development with WorkTrees
```
Main Branch
  ├── trees/feature-A/  → Claude 1 working
  ├── trees/feature-B/  → Claude 2 working
  ├── trees/feature-C/  → Claude 3 working
  └── trees/feature-D/  → Claude 4 working
      ↓ (all complete)
Main Branch (all merged together!)
```

## 🚀 Quick Start

### 1. Create Multiple WorkTrees

From your main project (in Claude Code):

```bash
# Create WorkTree for adding tests
/project:create-worktree add-tests

# Create WorkTree for adding logging
/project:create-worktree add-logging

# Create WorkTree for new feature
/project:create-worktree new-feature

# Create WorkTree for bug fix
/project:create-worktree fix-bug
```

**What happens:**
- Creates `trees/add-tests/` directory with full project copy
- Creates `add-tests` branch
- Opens new VS Code window for that WorkTree
- Links shared dependencies (venv, __pycache__, etc.)

### 2. Launch Claude in Each WorkTree

In each new VS Code window:

1. Open terminal
2. Run `clod` to start Claude Code
3. Give Claude a specific task

**Example tasks:**
```
# In trees/add-tests/
"Add comprehensive tests for the document conversion tool"

# In trees/add-logging/
"Add structured logging to all MCP server operations"

# In trees/new-feature/
"Add a new tool to extract images from PDFs"

# In trees/fix-bug/
"Fix the error handling in document_utils.py"
```

### 3. Let Them Work!

All Claude instances work **simultaneously** and **independently**:
- No file conflicts
- No blocking each other
- Each commits to their own branch

### 4. Merge Everything Back

From your **main** project (original window):

```bash
# Merge each completed feature
/project:merge-worktree add-tests
/project:merge-worktree add-logging
/project:merge-worktree new-feature
/project:merge-worktree fix-bug
```

Claude will:
- Review the changes
- Merge the branch
- Resolve any conflicts automatically
- Run tests to verify

### 5. Clean Up

```bash
/project:cleanup-worktrees
```

Removes all WorkTrees and branches, leaving you with a clean merged result!

## 📋 Custom Commands

Three custom commands are available (no need to remember the Git syntax):

### `/project:create-worktree <branch-name>`
Creates a new WorkTree for parallel development.

**Example:**
```bash
/project:create-worktree feature-xyz
```

**What it does:**
1. Creates `trees/feature-xyz/` directory
2. Creates and checks out `feature-xyz` branch
3. Symlinks dependencies (venv, __pycache__)
4. Opens new VS Code window

### `/project:merge-worktree <branch-name>`
Merges a WorkTree branch back into main.

**Example:**
```bash
/project:merge-worktree feature-xyz
```

**What it does:**
1. Reviews changes in the branch
2. Switches to main branch
3. Merges the feature branch
4. Resolves conflicts if needed
5. Runs tests to verify

### `/project:cleanup-worktrees`
Removes all WorkTrees and cleans up.

**What it does:**
1. Lists all WorkTrees
2. Removes each WorkTree directory
3. Deletes merged branches
4. Cleans up the trees/ directory

## 💡 Real-World Examples

### Example 1: Four Parallel Features

**Scenario:** You need to add tests, logging, two new tools

```bash
# Terminal 1 (main project)
clod
/project:create-worktree add-tests
/project:create-worktree add-logging
/project:create-worktree tool-image-extract
/project:create-worktree tool-summarize

# Now you have 4 new VS Code windows!

# Terminal 2 (trees/add-tests/)
clod
"Add comprehensive test suite for document_utils.py"

# Terminal 3 (trees/add-logging/)
clod
"Add structured logging with Python logging module to document_server.py"

# Terminal 4 (trees/tool-image-extract/)
clod
"Create a new MCP tool to extract images from PDF files"

# Terminal 5 (trees/tool-summarize/)
clod
"Create a tool to summarize markdown documents using Claude"

# ... wait for all to complete ...

# Back in Terminal 1 (main project)
/project:merge-worktree add-tests
/project:merge-worktree add-logging
/project:merge-worktree tool-image-extract
/project:merge-worktree tool-summarize

# Clean up
/project:cleanup-worktrees

# Done! All 4 features implemented and merged!
```

### Example 2: Documentation Sprint

```bash
# Create WorkTrees for documentation tasks
/project:create-worktree docs-api
/project:create-worktree docs-setup
/project:create-worktree docs-examples

# In each WorkTree, ask Claude to write specific docs
# trees/docs-api/: "Write API documentation for all MCP tools"
# trees/docs-setup/: "Write detailed setup guide"
# trees/docs-examples/: "Create 10 usage examples"

# Merge all docs back
/project:merge-worktree docs-api
/project:merge-worktree docs-setup
/project:merge-worktree docs-examples
```

### Example 3: Testing & Bug Fixes

```bash
# Create WorkTrees for different areas
/project:create-worktree test-document-server
/project:create-worktree test-utils
/project:create-worktree fix-pdf-parsing
/project:create-worktree fix-word-headers

# Each Claude instance focuses on one area
# All work happens simultaneously
# Merge everything when done
```

## ⚙️ Configuration

The custom commands are stored in `.claude/commands/`:

```
.claude/
└── commands/
    ├── create-worktree.md     # Creates new WorkTree
    ├── merge-worktree.md      # Merges WorkTree back
    └── cleanup-worktrees.md   # Cleans up all WorkTrees
```

These commands use `$ARGUMENTS` to dynamically insert branch names.

## 🔧 Troubleshooting

### WorkTree creation fails
**Issue:** "fatal: 'trees/feature' already exists"
**Solution:** Remove the existing WorkTree first
```bash
git worktree remove trees/feature
```

### Can't merge - conflicts
**Issue:** Merge conflicts when merging WorkTree
**Solution:** Claude will handle this automatically when you run `/project:merge-worktree`
- Claude reads both versions
- Combines changes appropriately
- Runs tests to verify

### Dependencies missing in WorkTree
**Issue:** "Module not found" in new WorkTree
**Solution:** The create-worktree command symlinks common dependencies
- venv/
- __pycache__/
- node_modules/

If you need additional directories, edit `.claude/commands/create-worktree.md`

### WorkTree won't remove
**Issue:** "Cannot remove worktree"
**Solution:** Use force flag
```bash
git worktree remove trees/feature --force
```

## 📊 Performance Tips

### Optimal Number of Instances
- **3-4 instances:** Ideal for most developers
- **5-6 instances:** For experienced users
- **7+ instances:** Only if you can manage the context switching

### Task Distribution
**Good tasks for parallel work:**
- ✅ Independent features
- ✅ Different files/modules
- ✅ Testing different components
- ✅ Documentation tasks
- ✅ Bug fixes in separate areas

**Avoid parallel work on:**
- ❌ Same file/function
- ❌ Highly interdependent features
- ❌ Refactoring shared code

### Memory Considerations
Each Claude instance + VS Code window uses resources:
- ~200-500 MB per instance
- Monitor your system performance
- Close WorkTrees you're not actively using

## 🎓 Advanced Patterns

### Staged Rollout
```bash
# Phase 1: Core features
/project:create-worktree core-feature-a
/project:create-worktree core-feature-b
# Wait, test, merge

# Phase 2: Dependent features (after Phase 1 merges)
/project:create-worktree enhancement-a
/project:create-worktree enhancement-b
```

### Testing Pipeline
```bash
# Create test WorkTrees
/project:create-worktree unit-tests
/project:create-worktree integration-tests
/project:create-worktree e2e-tests

# Each Claude writes comprehensive tests for one layer
# Merge all tests together for full coverage
```

### Documentation Sprint
```bash
# Parallel documentation
/project:create-worktree docs-readme
/project:create-worktree docs-api
/project:create-worktree docs-tutorials
/project:create-worktree docs-troubleshooting
```

## 📈 Productivity Gains

### Without Parallel Development
```
Feature A: 30 minutes
Feature B: 30 minutes  (wait for A)
Feature C: 30 minutes  (wait for B)
Feature D: 30 minutes  (wait for C)
Total: 2 hours
```

### With Parallel Development
```
Feature A: 30 minutes  }
Feature B: 30 minutes  } All parallel
Feature C: 30 minutes  }
Feature D: 30 minutes  }
Merging:   10 minutes
Total: 40 minutes
```

**Result: 3x faster development! 🚀**

## 🎯 Best Practices

1. **Clear task boundaries** - Give each Claude instance a specific, focused task
2. **Review before merging** - Check each WorkTree's changes before merge
3. **Test after merging** - Always run tests after merging multiple branches
4. **Clean up regularly** - Don't let WorkTrees accumulate
5. **Descriptive names** - Use clear branch names like `add-logging` not `feature1`
6. **Commit often** - Each Claude should commit when done
7. **Monitor progress** - Check in on each instance periodically

## 🔗 Resources

- **Git WorkTrees Docs:** https://git-scm.com/docs/git-worktree
- **Claude Code Docs:** https://docs.anthropic.com
- **MCP Protocol:** https://modelcontextprotocol.io

## 🎉 Success Stories

With this setup, you can accomplish in **1 hour** what might take **4 hours** sequentially:

- ✅ Add 4 new MCP tools
- ✅ Write comprehensive tests
- ✅ Add logging and monitoring
- ✅ Update documentation
- ✅ Fix multiple bugs

All running in parallel, all merging cleanly, all tested and verified.

**Welcome to the future of software development!** 🚀

---

**Next Steps:**
1. Try creating your first WorkTree: `/project:create-worktree my-first-feature`
2. Give Claude a task in that WorkTree
3. Merge it back when complete: `/project:merge-worktree my-first-feature`
4. Scale up to 3-4 parallel features!

Happy parallel coding! 🎊
