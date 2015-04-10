#!/bin/sh
# @Author: Guodong Wang
# @Date:   2015-04-10 10:53:07
# @Last Modified by:   Guodong Wang
# @Last Modified time: 2015-04-10 10:59:07

s3a_tar_s3_key="s3://warehouse-tmp/spark-ec2/s3a-package/s3a.tgz"
s3a_local_dir=/root/s3a-install
s3a_lib_dir=/usr/lib/s3a

function die
{
  echo "$*"
  exit 255
}

rm -rf $s3a_local_dir
mkdir -p $s3a_local_dir

aws s3 cp $s3a_tar_s3_key $s3a_local_dir/s3a.tgz || die "download s3a.tgz fails."

rm -rf $s3a_lib_dir
mkdir -p $s3a_lib_dir
cd $s3a_lib_dir
tar xzvf $s3a_local_dir/s3a.tgz || die "untar s3a.tgz fails."
