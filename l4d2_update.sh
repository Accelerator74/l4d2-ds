#!/bin/bash
screen -S L4D2_DS -X quit
./steamcmd.sh +login anonymous +force_install_dir ../l4d2_ds +app_update 222860 +quit