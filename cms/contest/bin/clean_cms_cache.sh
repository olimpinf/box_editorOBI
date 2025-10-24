#!/bin/bash

num_workers=12

for ((i=0; i<num_workers; i++)); do
    find /var/local/cache/cms/fs-cache-Worker-$i/ -type f -mmin +59 -delete 
done
