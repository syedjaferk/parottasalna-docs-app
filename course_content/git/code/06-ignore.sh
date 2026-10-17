git config --global user.name "Dev User"
git config --global user.email "dev@example.com"
git config --global init.defaultBranch main
git init -q shop
cd shop
touch app.py secrets.env debug.log error.log notes.txt important.txt
mkdir build && touch build/out.bin

echo '--- before .gitignore: everything is untracked'
git status -s

printf '%s\n' '# secrets' 'secrets.env' '' '# logs' '*.log' '' '# build output' 'build/' '' '# all text files, except one' '*.txt' '!important.txt' > .gitignore
echo '--- after .gitignore'
git status -s

echo '--- why is a file ignored? (-v shows the rule)'
git check-ignore -v debug.log build/out.bin notes.txt
echo '--- is important.txt ignored? (exit code 1 = no)'
git check-ignore important.txt; echo "exit code $?"

echo '--- files you can see in the folder but Git skips'
git status --ignored -s | grep '^!!'

echo '--- an ignore rule only affects UNTRACKED files'
git add -f secrets.env
git commit -q -m "Oops, committed secrets"
echo "password=123" >> secrets.env
git status -s
echo '--- fix: stop tracking it, keep the file on disk'
git rm -q --cached secrets.env
git commit -q -m "Stop tracking secrets.env"
git status -s

echo '--- a private rule for this clone only (never committed)'
echo "scratch/" >> .git/info/exclude
mkdir scratch && touch scratch/ideas.txt
git status -s
