#! /bin/bash

function testing () {
  cd $1
  echo $1
  python3 ../../src/rmlviewer.py --mapping mapping.ttl
  java -jar ../mappingweaver.jar -m ./mapping_without_views.ttl > ./output_test.nq
  if [ -f output.nq ]; then
    result=`python3 ../compare.py output.nq output_test.nq`
  elif [ ! -s output_test.nq ]; then
    result="TRUE"
  else
    result="FALSE"
  fi
  echo  "|" $dir "|" $result "|">> ../result.md
  rm view* mapping_without_views.ttl output_test.nq
  cd ..
}

for dir in ./*/ ;
do
  echo "testing $dir";
  testing $dir
done

