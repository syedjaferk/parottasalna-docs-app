docker rm -f dm-shell >/dev/null 2>&1
echo '--- run a command and let the container disappear (--rm)'
docker run --rm alpine echo "Hello, Docker!"
echo '--- the same container has its own hostname and its own process list'
docker run --rm alpine sh -c 'hostname; ps'
echo '--- a container lives only as long as its main process'
docker run --name dm-shell alpine sh -c 'echo working; sleep 1; echo done'
docker ps -a --filter name=dm-shell --format '{{.Names}}: {{.Status}}'
echo '--- run a second command inside a running container (exec)'
docker run -d --name dm-shell2 alpine sleep 30 >/dev/null
docker exec dm-shell2 sh -c 'echo "I am inside: $(hostname)"; cat /etc/alpine-release'
docker rm -f dm-shell dm-shell2 >/dev/null
