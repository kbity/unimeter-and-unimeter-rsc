#!/bin/bash
nano acronyms.txt
sort < acronyms.txt | uniq | sort | uniq > a.txt
mv a.txt acronyms.txt
