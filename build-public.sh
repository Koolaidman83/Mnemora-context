#!/usr/bin/env bash
set -eu

mkdir -p site-public

for f in index.html llms.txt llms-full.txt \
         knowledge-index.json README.md BIO.md \
         robots.txt manifest.json
do
    if [ -f "$f" ]; then
        cp "$f" site-public/
    fi
done

for d in knowledge context
do
    if [ -d "$d" ]; then
        cp -R "$d" site-public/
    fi
done
