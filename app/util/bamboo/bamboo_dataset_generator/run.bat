@if [%DEBUG%] == [] @echo off
IF "%BAMBOO_TOKEN%"=="" (echo "BAMBOO_TOKEN is not set" && exit /b)
mvn compile exec:java -Dexec.mainClass="bamboogenerator.Main"