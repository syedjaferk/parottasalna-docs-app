echo '--- host kernel'
uname -r
echo '--- kernel seen inside an alpine container'
docker run --rm alpine uname -r
echo '--- which Linux distribution is inside?'
docker run --rm alpine head -1 /etc/os-release
echo '--- image size'
docker images alpine --format '{{.Repository}}:{{.Tag}}  {{.Size}}'
echo '--- how long does a container take to start, run and exit?'
TIMEFORMAT='real %3Rs'
time docker run --rm alpine echo "hello from a container"
