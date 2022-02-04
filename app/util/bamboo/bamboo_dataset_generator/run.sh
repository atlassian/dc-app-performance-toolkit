#!/bin/sh
[ -z "$BAMBOO_TOKEN" ] && echo "BAMBOO_TOKEN is not set" && exit
mvn compile exec:java -Dexec.mainClass="bamboogenerator.Main"
