git --version

echo '--- 1. global identity, used by every repository on this computer'
git config --global user.name "DevUser"
git config --global user.email "devuser@example.com"
git config --global init.defaultBranch main
git config --global --list

echo '--- 2. a project that must use a different identity'
git init -q MyProject
cd MyProject
git config user.name "ProjectUser"
git config user.email "projectuser@example.com"

echo '--- who wins inside this project? (and where each value comes from)'
git config --show-origin --get-regexp '^user\.'
echo '--- the value Git will really use'
git config user.name

echo '--- the identity lands on every commit'
git commit -q --allow-empty -m "First commit"
git log -1 --format='%an <%ae>'
