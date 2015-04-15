#!/bin/sh
# @Author: Guodong Wang
# @Date:   2015-02-27 17:58:04
# @Last Modified by:   Guodong Wang
# @Last Modified time: 2015-04-15 10:56:26

function die()
{
  echo "$*"
  exit 1
}

download_dir=/root/aws-hadoop/

rm -rf $download_dir
mkdir -p $download_dir
echo "change working dir to $download_dir"
cd $download_dir
rm -rf aws-hadoop-conf
git clone -b master git@git.llsapp.com:data-pipeline/aws-hadoop-conf.git


hadoop_conf_dir=/root/hadoop/etc/hadoop
rm -rf $hadoop_conf_dir
mkdir $hadoop_conf_dir || die "fail to create $hadoop_conf_dir"

mv aws-hadoop-conf/hadoop-conf/* $hadoop_conf_dir
