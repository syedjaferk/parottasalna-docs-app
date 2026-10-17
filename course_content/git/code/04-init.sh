mkdir MyProject
cd MyProject
git init

echo '--- is it a repository now?'
git status

echo '--- what did init create?'
ls -A
ls .git

echo '--- the default branch name is a setting'
git config --global init.defaultBranch main
git init -q ../Another
git -C ../Another branch --show-current

echo '--- running git in a folder that is not a repository'
cd /
git status 2>&1 | head -1
