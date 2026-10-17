cd "$(dirname "$0")/app"
docker rm -f dm-app >/dev/null 2>&1
echo '--- build the image'
docker build -q -t dm-app:1.0 . | sed 's/sha256:\(.\{12\}\).*/built image sha256:\1.../'
echo '--- the layers, one per Dockerfile instruction'
docker history dm-app:1.0 --format '{{.CreatedBy}}' | head -6
echo '--- run it and call it twice'
docker run -d --name dm-app -p 8089:8000 dm-app:1.0 >/dev/null
sleep 1
curl -s http://localhost:8089/
curl -s http://localhost:8089/
echo '--- change a setting without rebuilding (-e)'
docker rm -f dm-app >/dev/null
docker run -d --name dm-app -e GREETING=Vanakkam -p 8089:8000 dm-app:1.0 >/dev/null
sleep 1
curl -s http://localhost:8089/
echo '--- build again with no changes: every step comes from the cache'
docker build --progress=plain -t dm-app:1.0 . 2>&1 | grep CACHED | sed 's/^#[0-9]* //'
docker rm -f dm-app >/dev/null
