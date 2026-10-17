docker rm -f dm-ticker >/dev/null 2>&1
echo '--- start a container in the background with a name'
docker run -d --name dm-ticker alpine sh -c 'for i in 1 2 3 4 5; do echo "tick $i"; sleep 1; done; sleep 60' >/dev/null
sleep 6
docker ps --filter name=dm-ticker --format '{{.Names}}  {{.Image}}  {{.Status}}'
echo '--- read its output with logs'
docker logs dm-ticker
echo '--- inspect: pull single facts out of the JSON'
docker inspect --format 'state={{.State.Status}}  image={{.Config.Image}}  cmd={{.Config.Cmd}}' dm-ticker
echo '--- stop and remove'
docker stop dm-ticker >/dev/null
docker ps -a --filter name=dm-ticker --format '{{.Names}}: {{.Status}}' | sed 's/Exited (\([0-9]*\)) .*/Exited (\1)/'
docker rm dm-ticker
echo '--- names must be unique'
docker run -d --name dm-ticker alpine sleep 5 >/dev/null
docker run -d --name dm-ticker alpine sleep 5 2>&1 | head -1 | sed 's/by container "[0-9a-f]*"/by container "<id>"/; s/^docker: //'
docker rm -f dm-ticker >/dev/null
