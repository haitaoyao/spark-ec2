#!/bin/sh
# @Author: Guodong Wang
# @Date:   2015-02-27 17:58:04
# @Last Modified by:   Guodong Wang
# @Last Modified time: 2015-03-10 15:03:41

function die()
{
  echo "$*"
  exit 1
}

download_dir=/root/aws-hadoop/

cd $download_dir
rm -rf hadoop_conf
wget --reject "index.html*" -nH -r --no-parent http://ip-172-31-7-86/hadoop_conf/

hadoop_conf_dir=/root/hadoop/etc/hadoop
rm -rf $hadoop_conf_dir
mkdir $hadoop_conf_dir || die "fail to create $hadoop_conf_dir"

mv hadoop_conf/* $hadoop_conf_dir
rmdir hadoop_conf