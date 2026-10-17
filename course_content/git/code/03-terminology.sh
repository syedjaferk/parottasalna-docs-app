git config --global user.name "Dev User"
git config --global user.email "dev@example.com"
git config --global init.defaultBranch main

echo '--- repository: a folder plus a hidden .git folder'
git init -q recipes
cd recipes
ls -a
ls .git | head -8

echo '--- commit: a snapshot with a message'
echo "tea, water, milk" > chai.txt
git add chai.txt
git commit -q -m "Add chai recipe"
git log --oneline

echo '--- branch: a parallel line of work'
git switch -q -c add-coffee
echo "coffee, milk, sugar" > coffee.txt
git add coffee.txt
git commit -q -m "Add coffee recipe"
git branch

echo '--- merge: bring the branch back to main'
git switch -q main
ls
git merge -q add-coffee
ls
git log --oneline

echo '--- clone: a full copy, with its history, and a remote called origin'
cd ..
git clone -q recipes recipes-copy
cd recipes-copy
git remote -v
git log --oneline | wc -l
