#!/bin/bash

case "$1" in 
	registry)
		cp *.csv ./registry-data/
		echo "copied registry data-------"
		sleep 5
		;;

	bgp)
		rm ./bgp-data/*
		cp *.gz ./bgp-data/
		echo "copied bgp data-----"
		;;
	*)
		cp *.csv ./registry-data/
        	echo "copied registry data-------"
	        sleep 5
		cp *.gz ./bgp-data/
	        echo "copied bgp data-----"
		exit 1
esac
