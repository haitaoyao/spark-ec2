#!/bin/sh
# @Author: Guodong Wang
# @Date:   2015-03-25 10:27:46
# @Last Modified by:   Guodong Wang
# @Last Modified time: 2015-03-25 14:12:47

cdir="/root/spark-ec2/heap-dump-upload"

/bin/cp $cdir/upload_spark_heap_dump.py /usr/local/bin/
/bin/cp $cdir/upload-spark-heap-dump /usr/local/bin/
/bin/cp $cdir/upload-spark-cluster-heap-dump /usr/local/bin/

chmod a+x /usr/local/bin/upload-spark-heap-dump
chmod a+x /usr/local/bin/upload-spark-cluster-heap-dump