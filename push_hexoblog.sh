#!/bin/sh

git config --global user.name "DeppWang"
git config --global user.email "deppwxq@gmail.com"

cd /home/runner/work/Obsidian/Obsidian/HexoBlog-Resp/
git add .
git commit -m "Updated: `date +'%Y-%m-%d %H:%M:%S'`"
git push origin master
