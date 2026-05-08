#! /bin/bash

function testing () {
  test -f ./burp.jar || curl -LO https://github.com/kg-construct/BURP/releases/download/v0.1.1/burp.jar
  cd $1
  echo $1
  node ../../../normalize-rml/bin/cli.js mapping.ttl rmlkgc > mapping_n.ttl
  python3 ../../src/view_to_json.py --mapping mapping_n.ttl
  java -jar ../burp.jar -m ./mapping_without_views.ttl -o ./output_test.nq
  #java -jar ../rmlmapper.jar -m ./mapping_without_views.ttl -o ./output_test.nq
 # result=`python3 ../compare.py output.nq output_test.nq`
 # echo  "|" $dir "|" $result "|">> ../result.md
 # rm view* mapping_without_views.ttl mapping_n.ttl output_test.nq
  cd ..
}

testing "test"
