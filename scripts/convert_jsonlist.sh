#!/bin/bash

in_file=$1

sed -i -e '1i[' -e '$a]' -e 's/}{/},{/g' ${in_file}
