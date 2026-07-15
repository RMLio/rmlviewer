#! /bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

function testing () {
  case_dir="$1"
  cd "$case_dir"
  echo "$case_dir"
  python3 "${REPO_ROOT}/src/rmlviewer.py" --mapping mapping.ttl
  java -jar "${SCRIPT_DIR}/mappingweaver.jar" -m ./mapping_without_views.ttl > ./output_test.nq
  if [ -f output.nq ]; then
    result=$(python3 "${SCRIPT_DIR}/compare.py" output.nq output_test.nq)
  elif [ ! -s output_test.nq ]; then
    result="TRUE"
  else
    result="FALSE"
  fi
  echo "| $(basename "$case_dir") | $result |" >> "${SCRIPT_DIR}/result.md"
  rm view* mapping_without_views.ttl output_test.nq
  cd "$SCRIPT_DIR"
}

test_mappingdirectory_outside_case_dir () {
  case_dir="${SCRIPT_DIR}/RMLLVTC0010d"
  out_dir=$(mktemp -d)
  result="FALSE"

  if (cd "${REPO_ROOT}" && python3 "${REPO_ROOT}/src/rmlviewer.py" --mapping "${case_dir}/mapping.ttl" --output_dir "${out_dir}" >/dev/null 2>&1); then
    if [ -f "${out_dir}/mapping_without_views.ttl" ] && [ -f "${out_dir}/view0.json" ]; then
      result="TRUE"
    fi
  fi

  echo "| REGRESSION_MAPPING_DIRECTORY_OUTSIDE | $result |" >> "${SCRIPT_DIR}/result.md"
  rm -rf "${out_dir}"
}

test_missing_root_uses_cwd_default () {
  tmp_case_dir=$(mktemp -d)
  cp -r "${SCRIPT_DIR}/RMLLVTC0000a/." "${tmp_case_dir}/"
  sed -i '/rml:root rml:MappingDirectory/d' "${tmp_case_dir}/mapping.ttl"

  fail_from_repo="FALSE"
  succeed_from_case_dir="FALSE"

  if ! (cd "${REPO_ROOT}" && python3 "${REPO_ROOT}/src/rmlviewer.py" --mapping "${tmp_case_dir}/mapping.ttl" --output_dir "${tmp_case_dir}/out_fail" >/dev/null 2>&1); then
    fail_from_repo="TRUE"
  fi

  if (cd "${tmp_case_dir}" && python3 "${REPO_ROOT}/src/rmlviewer.py" --mapping mapping.ttl --output_dir "${tmp_case_dir}/out_ok" >/dev/null 2>&1); then
    if [ -f "${tmp_case_dir}/out_ok/mapping_without_views.ttl" ] && [ -f "${tmp_case_dir}/out_ok/view0.json" ]; then
      succeed_from_case_dir="TRUE"
    fi
  fi

  result="FALSE"
  if [[ "$fail_from_repo" == "TRUE" && "$succeed_from_case_dir" == "TRUE" ]]; then
    result="TRUE"
  fi

  echo "| REGRESSION_MISSING_ROOT_CWD_DEFAULT | $result |" >> "${SCRIPT_DIR}/result.md"
  rm -rf "${tmp_case_dir}"
}

cd "$SCRIPT_DIR"
for dir in "$SCRIPT_DIR"/*/ ;
do
  echo "testing $dir"
  testing $dir
done

test_mappingdirectory_outside_case_dir
test_missing_root_uses_cwd_default

