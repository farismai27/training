# Merge WorkTree Command

Please merge the changes from the `$ARGUMENTS` WorkTree branch back into the main branch.

Follow these steps:

1. **Check the current branch status** to ensure we're in a clean state

2. **Review the changes** from the WorkTree branch:
   - Navigate to `trees/$ARGUMENTS`
   - View the most recent commit to understand what was implemented
   - Review the git log for the branch

3. **Switch to the main branch** (or the base branch you're merging into)

4. **Merge the branch**:
   - Use `git merge $ARGUMENTS` to merge the changes
   - If there are merge conflicts, resolve them carefully by:
     - Examining the conflicting files
     - Understanding what each branch changed
     - Combining the changes appropriately
     - Testing that the merged code works correctly

5. **Verify the merge**:
   - Check that all tests still pass
   - Ensure no functionality was broken
   - Review the combined changes

6. **Commit the merge** if there were conflicts that needed manual resolution

Commands to use:
```bash
# Check current status
git status

# View the changes in the worktree
cd trees/$ARGUMENTS
git log -1 --stat
cd ../..

# Ensure we're on the main branch
git checkout claude/import-vs-workspace-kobAs

# Merge the branch
git merge $ARGUMENTS

# If there are conflicts, resolve them and then:
# git add <resolved-files>
# git commit -m "Merge $ARGUMENTS branch"

# Verify everything works
python -m pytest tests/ -v
```

After completion, confirm:
- Branch `$ARGUMENTS` successfully merged
- No conflicts remain (or conflicts were resolved)
- Tests pass
- Code is in a working state

The WorkTree changes are now integrated into the main branch!
