# Create WorkTree Command

Please follow these steps to create a new Git WorkTree for parallel development:

1. **Create a new Git WorkTree** in the `trees/$ARGUMENTS` directory based on a new branch called `$ARGUMENTS`

2. **Create the necessary symlinks** for dependencies that aren't tracked by Git:
   - Symlink `__pycache__` directory if it exists
   - Symlink any virtual environment directories (venv, .venv) if they exist
   - Symlink `node_modules` if it exists

3. **Verify the WorkTree was created** by listing the contents of the trees directory

4. **Open a new code editor instance** inside the newly created WorkTree directory at `trees/$ARGUMENTS`

Commands to use:
```bash
# Create the worktree
git worktree add -b $ARGUMENTS trees/$ARGUMENTS

# Create symlinks for common dependencies (if they exist)
[ -d __pycache__ ] && ln -s ../../__pycache__ trees/$ARGUMENTS/__pycache__
[ -d .venv ] && ln -s ../../.venv trees/$ARGUMENTS/.venv
[ -d venv ] && ln -s ../../venv trees/$ARGUMENTS/venv
[ -d node_modules ] && ln -s ../../node_modules trees/$ARGUMENTS/node_modules

# Open the new worktree in your editor
code trees/$ARGUMENTS
```

After completion, confirm:
- WorkTree directory created at `trees/$ARGUMENTS`
- New branch `$ARGUMENTS` created
- Symlinks created for dependencies
- New editor window opened

The new WorkTree is now ready for isolated development work!
