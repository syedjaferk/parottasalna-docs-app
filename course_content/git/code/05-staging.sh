git config --global user.name "Dev User"
git config --global user.email "dev@example.com"
git config --global init.defaultBranch main
git init -q site
cd site
touch app.js style.css README.md

echo '--- 1. stage one file only'
git add style.css
git status -s

echo '--- 2. stage everything except README.md'
git add -- ':!README.md'
git status -s

echo '--- 3. stage only part of a file (git add -p)'
git commit -q -m "Start the site"
seq -f 'line %g' 1 20 > style.css
git add style.css && git commit -q -m "Add styles"
sed -i -e '1s/.*/line 1 (edited)/' -e '20s/.*/line 20 (edited)/' style.css
printf 'y\nn\n' | git add -p style.css | grep '^[-+@]\|Stage'
git status -s
echo '--- staged part versus the rest'
git diff --staged --stat
git diff --stat

echo '--- take a file back out of the staging area'
git restore --staged style.css
git status -s
