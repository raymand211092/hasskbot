# HASSkbot - home-assistant ask bot

[![Matrix Channel](https://img.shields.io/matrix/hasskbot:fiksel.info.svg?label=%23hasskbot%3Afiksel.info&logo=matrix&server_fqdn=matrix.fiksel.info)](https://matrix.to/#/#hasskbot:fiksel.info)

Opsdroid bot, which reacts to a home-assistant entity state change (like person tracker, or light) and asks for confirmation if it should run additional home-assistant atomation.
Matrix reactions are used for confirming or canceling action.

![screenshot01](images/screenshot01.png)
![screenshot02](images/screenshot02.png)

# Running

## docker-compose

* Clone the repository
```
git clone https://gitlab.com/olegfiksel/hasskbot.git
cd hasskbot
```
* Create new config file (copy an example)
```
cp sample-config.yaml configuration.yaml
```
* Adjust the config `configuration.yaml` to your needs
* Create secrets (copy an example)
```
cp secrets-example.env secrets.env
```
* Start the bot
```
docker-compose up -d
docker-compose logs -f
```

# Troubleshooting

* Home-assistant `zone.home`, used in the example config, has a value (number of persons in the zone) only since [2022.4](https://www.home-assistant.io/blog/2022/04/06/release-20224/#zones-now-have-a-state)
