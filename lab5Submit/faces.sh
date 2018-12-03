#!/bin/bash

# Script for executing the java version of Faces 
# Usage:
# bash faces.sh <training_file> <facit_file> <test_file>

# Author: Ola Ringdahl

start_dir=$PWD # current directory
base_dir="$(dirname "$0")" # the location of this script

cd $base_dir

# start with removing any class files and re-compile the code:
rm -f *.class
javac *.java

cd $start_dir 
 
# Run the face detection
java -cp $base_dir: Faces $1 $2 $3

