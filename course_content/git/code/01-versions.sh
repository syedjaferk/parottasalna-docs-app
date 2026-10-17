git config --global user.name "Dev User"
git config --global user.email "dev@example.com"
git config --global init.defaultBranch main

echo '--- the old way: copies with hopeful names'
echo "version 1" > report.txt
cp report.txt report_final.txt
cp report.txt report_final_v2.txt
cp report.txt report_final_v2_REALLY_final.txt
ls

echo '--- the Git way: one file, a history'
rm report_final*.txt
git init -q
git add report.txt
git commit -q -m "First draft of the report"
echo "version 2, with the summary added" > report.txt
git commit -q -am "Add summary"
echo "version 3, summary shortened" > report.txt
git commit -q -am "Shorten summary"
git log --format='%h  %an  %s'

echo '--- what changed in the last step?'
git diff HEAD~1 HEAD --stat
git diff HEAD~1 HEAD | tail -4

echo '--- go back to the first draft, without losing anything'
git show HEAD~2:report.txt
