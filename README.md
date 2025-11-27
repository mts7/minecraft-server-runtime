# minecraft-server-runtime
Minecraft Docker environment for Crafty Controller, updates, and log listeners.

## Keep In Mind

### servers/{UUID}/config/Geyser/config.yml needs specific values

```yaml
bedrock:
  address: 0.0.0.0
  port: 19132

remote:
  address: 127.0.0.1
  port: 25565

advanced:
  use-proxy-protocol: true

java:
  auth-type: floodgate
```

### server.properties update

Change property `network-compression-threshold` value from 512 to -1.

### Install Proxy Protocol Support server mod

[Proxy Protocol Support -- Modrinth](https://modrinth.com/mod/proxy-protocol-support)

Add Docker subnet to `config/proxy_protocol_support.json`.

```json
{
  "enableProxyProtocol": true,
  "proxyServerIPs": [
    "127.0.0.1",
    "172.18.0.0/16"
  ],
  "directAccessIPs": [
    "127.0.0.1",
    "172.18.0.0/16",
    "192.168.0.0/16"
  ],
  "whitelistTCPShieldServers": false
}
```
Use `docker network inspect {NETWORK_NAME} | grep Subnet` to determine the
subnet to add.


## Docker Commands

These commands assume execution from the same directory as the README file.

### Stop and Remove All

```shell
docker compose down
docker compose rm -f
```

### Start All (and Remove Orphans)

The last two parameters are not necessary, though they can help.

```shell
docker compose up -d --force-recreate --remove-orphans
```

### Update Crafty

```shell
docker pull
docker compose down
docker compose up -d
```

### Determine Networking Status

```shell
docker network ls
docker network inspect {NETWORK_NAME}
```