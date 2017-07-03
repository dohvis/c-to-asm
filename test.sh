#!/bin/bash
while IFS= read -r line; do
   if [ $line == "Hello" ]; then
        return 1;
   fi
done
