#!/bin/sh
# @Author: Guodong Wang
# @Date:   2015-02-27 17:58:04
# @Last Modified by:   Guodong Wang
# @Last Modified time: 2015-04-01 20:04:02

function die()
{
  echo "$*"
  exit 1
}

download_dir=/root/aws-hadoop/

cd $download_dir
rm -rf aws-hadoop-conf
git clone -b s3a git@git.llsapp.com:data-pipeline/aws-hadoop-conf.git


hadoop_conf_dir=/root/hadoop/etc/hadoop
rm -rf $hadoop_conf_dir
mkdir $hadoop_conf_dir || die "fail to create $hadoop_conf_dir"

mv aws-hadoop-conf/hadoop_conf/* $hadoop_conf_dir