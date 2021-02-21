#!/bin/bash

help() {
    echo "To use this command you must supply the number of pokemon you want to start with tag -p";
    echo "and the number of pokemons that you want to write in the excelsheet with the tag -n";
    echo ""
    echo "./script.sh -p <Pokemon_Start> -n <Pokemons>";
    }

while getopts ":n:p:h:" opt; do
    case "${opt}" in
        h)
            help
            ;;
        n)
            n=${OPTARG}

            if (("$n" < 0))
            then
                echo "The value of n cannot be lower than 0"
                exit 0
            fi
            
            echo ${n}
            ;;
        p)
            p=${OPTARG}
            if (("$p" < 0))
            then
                echo "The value of p cannot be lower than 0"
                exit 0
            fi
            echo ${p}
            ;;
        *)
            help
            ;;
    esac
done

url="https://pokeapi.co/api/v2/pokemon?limit=${n}&offset=${p}"

curl -H "Content-Type: application/json" $url > "./pokemons.json"

python pokemons.py