docker rm -f dm-v1 dm-v2 dm-b1 >/dev/null 2>&1
docker volume rm dm-data >/dev/null 2>&1
echo '--- data written in a container without a volume is lost with it'
docker run --name dm-v1 alpine sh -c 'echo "note 1" > /data.txt'
docker rm dm-v1 >/dev/null
docker run --rm alpine ls /data.txt 2>&1 | sed 's/^/new container: /'
echo '--- a named volume outlives the container'
docker volume create dm-data
docker run --rm -v dm-data:/data alpine sh -c 'echo "note 1" > /data/note.txt'
docker run --rm -v dm-data:/data alpine cat /data/note.txt
echo '--- two containers can share the same volume'
docker run --rm -v dm-data:/data alpine sh -c 'echo "note 2" >> /data/note.txt'
docker run --rm -v dm-data:/data alpine cat /data/note.txt
echo '--- list volumes'
docker volume ls --filter name=dm-data --format '{{.Driver}}  {{.Name}}'
echo '--- a bind mount shows a host folder inside the container'
mkdir -p /tmp/dm-bind && echo "from the host" > /tmp/dm-bind/hello.txt
docker run --rm -v /tmp/dm-bind:/mnt alpine cat /mnt/hello.txt
echo '--- clean up'
docker volume rm dm-data
rm -rf /tmp/dm-bind
