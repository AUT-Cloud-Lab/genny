#!/bin/bash

echo "Should activate the venv!"

# normals
cmd="python3 genny.py normal"
for mean in  0.75 1 1.25; do
    for sigma in 0.4;  do
        cur_cmd="${cmd} ${mean} ${sigma} "
        eval $cur_cmd

        if [ $? -ne 0 ]; then
            echo "Error in command: $cur_cmd"
            rm -rf out/*
            exit 1
        fi
    done
done

#V
## wavy
#cmd="python genny.py wavy"
#for base_usage in 0.5 1; do
#    for deployment_number in 1 2 3 4; do
#        cur_cmd="${cmd} ${base_usage} ${deployment_number} "
#        eval $cur_cmd
#
#        if [ $? -ne 0 ]; then
#            echo "Error in command: $cur_cmd"
#            rm -rf out/*
#            exit 1
#        fi
#
#    done
#done
