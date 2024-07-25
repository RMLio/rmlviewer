#! /bin/bash

function testing () {
  test -f ./burp.jar || curl -LO https://github.com/kg-construct/BURP/releases/download/v0.1.1/burp.jar
  cd $1
  echo $1
  python ../../view_to_csv.py --mapping mapping.ttl
  java -jar ../burp.jar -m ./mapping_without_views.ttl -o ./output_test.nq
  python ../compare.py output.nq output_test.nq
  rm view* mapping_without_views.ttl output_test.nq
  cd ..
}

testing ./RMLLVTC0001
testing ./RMLLVTC0002
testing ./RMLLVTC0003
testing ./RMLLVTC0004
testing ./RMLLVTC0005
testing ./RMLLVTC0006
testing ./RMLLVTC0007
testing ./RMLLVTC0008
testing ./RMLLVTC0009