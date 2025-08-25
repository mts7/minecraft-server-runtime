#!/bin/zsh

. .env

rm -rf ${CRAFTY_DIRECTORY}/docker/servers/${SERVER_ALTERNATE_UUID}/Fetchr-5.2.2/
unzip ${CRAFTY_DIRECTORY}/downloads/Fetchr-bingo/Fetchr-5.2.2.zip -d ${CRAFTY_DIRECTORY}/docker/servers/${SERVER_ALTERNATE_UUID}
