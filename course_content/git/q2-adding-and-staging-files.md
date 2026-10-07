# Q2 - Adding and Staging Files

### **Problem Statement**

1. **Add Specific Files**\
   Create two files, `app.js` and `style.css`. Use `git add` to stage only `style.css`. This allows selective addition of files to the staging area before committing.
2. **Interactive Staging**\
   Modify `style.css` and use `git add -p` to stage changes interactively. This lets you review and stage specific parts of a file.
3. **Stage All Files Except One**\
   Add all files in the folder to the staging area except `README.md`. Use a wildcard pattern to exclude the file, ensuring other files are prepared for commit.

### Solution

#### **1. Add Specific Files**

1. Create the files `app.js` and  `style.css`

```bash
touch app.js style.css
```

2. Stage only `style.css`

```bash
git add style.css
```

3. Verify the staged files

```bash
git status
```

```
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
    new file:   style.css

Untracked files:
  (use "git add <file>..." to include in what will be committed)
    app.js
```

#### **2. Interactive Staging**

1. Modify `style.css` (e.g., add some CSS code)

```css
/* Example content for style.css */
body {
    background-color: #f0f0f0;
}

```

2. Use interactive staging to review changes

```bash
git add -p style.css
```

3. Git will present changes in chunks and prompt for action

```
Stage this hunk [y,n,q,a,d,s,e,?]?
```

Actions:

* Press `y` to stage the current chunk.
* Press `n` to skip the current chunk.
* Press `q` to quit without staging more changes.

4. Verify the staged changes

```bash
git status
```

Example Output,&#x20;

```
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
    modified:   style.css
```

#### **3. Stage All Files Except One**

1. Create a new file `README.md` alongside `app.js` and `style.css`:

```bash
touch README.md
```

2. Use a wildcard pattern to stage all files except `README.md`:

```bash
git add -- ':!README.md'
```

3. Verify the staged files

```bash
git status
```

4. Verify the staged files

```bash
git status
```

5. Verify the status

```
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
    new file:   app.js
    new file:   style.css

Untracked files:
  (use "git add <file>..." to include in what will be committed)
    README.md
```
