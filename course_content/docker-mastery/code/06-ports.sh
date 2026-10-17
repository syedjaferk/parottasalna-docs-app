docker rm -f dm-web >/dev/null 2>&1
echo '--- run nginx and publish container port 80 as host port 8088'
docker run -d --name dm-web -p 8088:80 nginx:alpine >/dev/null
sleep 2
docker port dm-web
echo '--- request the page from the host'
curl -s -o /dev/null -w 'HTTP status: %{http_code}\n' http://localhost:8088/
curl -s http://localhost:8088/ | grep -o '<title>.*</title>'
echo '--- the access log shows that request'
docker logs dm-web 2>&1 | grep 'GET /' | sed 's/^\([0-9.]*\) .*\] "\(.*\)" \([0-9]*\) .*/client \1  "\2"  status \3/'
echo '--- without -p nothing is published'
docker run -d --name dm-web2 nginx:alpine >/dev/null
sleep 1
[ -z "$(docker port dm-web2)" ] && echo 'dm-web2 publishes no ports, so the host cannot reach it'
docker rm -f dm-web dm-web2 >/dev/null
