# Cleanup WorkTrees Command

Please clean up all WorkTrees that have been merged into the main branch.

Follow these steps:

1. **List all existing WorkTrees** to see what needs to be cleaned up

2. **For each WorkTree**, verify it has been merged:
   - Check if the branch has been merged into the main branch
   - Ensure no uncommitted changes exist in the WorkTree

3. **Remove the WorkTrees**:
   - Use `git worktree remove` for each WorkTree
   - Delete the corresponding branches if they're no longer needed

4. **Clean up the trees directory**:
   - Verify all WorkTree directories have been removed
   - Remove the trees directory if it's empty

5. **Prune any stale WorkTree references**

Commands to use:
```bash
# List all worktrees
git worktree list

# For each worktree in trees/, remove it
for worktree in trees/*; do
  if [ -d "$worktree" ]; then
    branch_name=$(basename "$worktree")
    echo "Removing worktree: $branch_name"
    git worktree remove "trees/$branch_name" || git worktree remove "trees/$branch_name" --force
  fi
done

# Delete the merged branches (optional, but clean)
git branch -d <branch-name>  # Or -D to force delete

# Prune stale worktree references
git worktree prune

# Remove trees directory if empty
[ -d trees ] && [ -z "$(ls -A trees)" ] && rmdir trees

# Verify cleanup
git worktree list
```

After completion, confirm:
- All WorkTrees have been removed
- Branches have been deleted (if desired)
- The trees directory is cleaned up
- No stale WorkTree references remain

Your repository is now clean and ready for the next round of parallel development!
