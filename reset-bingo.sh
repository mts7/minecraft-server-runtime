#!/bin/bash

. .env

#fetchr="Fetchr-5.3-beta5"
server="${CRAFTY_DIRECTORY}/docker/servers/${SERVER_ALTERNATE_UUID}"

#rm -rf ${server}/${fetchr}/
#unzip ${CRAFTY_DIRECTORY}/downloads/${fetchr}.zip -d ${server}

rm -rf ${server}/dynmap/web/tiles/fetchr_default/*

