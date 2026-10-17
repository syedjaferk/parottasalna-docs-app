echo '--- the client and the server (daemon) are separate programs'
docker version --format 'client {{.Client.Version}}   server {{.Server.Version}}'
echo '--- where the client sends its requests'
docker context inspect --format '{{.Endpoints.docker.Host}}'
echo '--- the daemon answers questions about itself'
docker info --format 'containers: {{.Containers}}   images: {{.Images}}   storage driver: {{.Driver}}'
echo '--- the client talking to the daemon with plain HTTP'
curl -s --unix-socket /var/run/docker.sock http://localhost/_ping; echo
