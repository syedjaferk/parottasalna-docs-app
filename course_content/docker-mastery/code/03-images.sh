docker rm -f dm-a dm-b >/dev/null 2>&1
echo '--- one image, two containers'
docker create --name dm-a alpine echo "container A" >/dev/null
docker create --name dm-b alpine echo "container B" >/dev/null
docker ps -a --filter name=dm- --format '{{.Names}}  {{.Image}}  {{.Status}}' | sort
echo '--- start them'
docker start -a dm-a
docker start -a dm-b
echo '--- changes live in the container, not in the image'
docker run --name dm-a2 alpine sh -c 'echo secret > /note.txt && cat /note.txt'
docker run --rm alpine cat /note.txt 2>&1 | sed 's/^/new container: /'
echo '--- the layers an image is built from'
docker history alpine:3.20 --format '{{.CreatedBy}}  {{.Size}}'
docker rm -f dm-a dm-b dm-a2 >/dev/null
