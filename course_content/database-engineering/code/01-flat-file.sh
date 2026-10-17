echo '--- films by Mani Ratnam'
grep 'Mani Ratnam' movies-flat.txt | cut -d'|' -f1
echo '--- rename "Mani Ratnam" to "Mani Rathnam" in the file'
sed 's/Mani Ratnam/Mani Rathnam/' movies-flat.txt > renamed.txt
grep -c 'Rathnam' renamed.txt
echo '--- a typo in ONE line goes unnoticed'
sed '2s/Ratnam/Ratnum/' movies-flat.txt | cut -d'|' -f2 | sort | uniq -c
rm renamed.txt
