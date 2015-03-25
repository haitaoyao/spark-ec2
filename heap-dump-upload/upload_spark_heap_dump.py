#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Guodong Wang
# @Date:   2015-03-25 10:31:57
# @Last Modified by:   Guodong Wang
# @Last Modified time: 2015-03-25 13:28:07

import boto
import logging
import time
import glob
import socket
import os

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s pid:%(process)d %(levelname)s %(module)s - %(message)s')

s3_aws_region = "cn-north-1"
s3_bucket_name = "warehouse-tmp"
s3_chunk_size = 50 * 1024 * 1024 # 50MB
hostname = socket.gethostname()
s3_heap_dump_key_prefix = "spark-heap-dump/%s/" % hostname
s3_gc_log_key_prefix = "spark-gc-log/%s/" % hostname
local_heap_dump_dir="/tmp"
local_gc_log_dir="/tmp"

logger = logging.getLogger("SparkHeapDumpUpload")


def copy_to_s3_simple(s3_bucket_object, local_file_path, s3_key, local_file_size):
    k = boto.s3.key.Key(s3_bucket_object)
    k.key = s3_key
    logger.info("Begin upload to s3. key:%s, local file:%s, size:%s" % (k, local_file_path, local_file_size))

    upload_size = k.set_contents_from_filename(local_file_path)
    logger.info("upload %s bytes to s3. local file:%s, size:%s" % (upload_size, local_file_path, local_file_size))
    return upload_size == local_file_size

def copy_to_s3_parallel(s3_bucket_object, local_file_path, s3_key, local_file_size):
    chunk_count = int(math.ceil(local_file_size / s3_chunk_size))
    mp = s3_bucket_object.initiate_multipart_upload(s3_key)
    try:
        # Send the file parts, using FileChunkIO to create a file-like object
        # that points to a certain byte range within the original file. We
        # set bytes to never exceed the original file size.
        for i in range(chunk_count + 1):
            logger.info("copy chunk-%s of file %s" % (i, local_file_path))
            offset = s3_chunk_size * i
            chunk_bytes_len = min(s3_chunk_size, local_file_size - offset)
            if chunk_bytes_len > 0:
                with FileChunkIO(local_file_path, 'r', offset=offset, 
                        bytes=chunk_bytes_len) as fp:
                    mp.upload_part_from_file(fp, part_num=i + 1)
        # Finish the upload
        mp.complete_upload()
        logger.info("upload %s complete!" % local_file_path)
        copy_succeed = True
    except Exception as e:
        logger.error("get exception during upload file '%s' parallelly to s3." % local_file_path)
        logger.error("Exception:%s" % e)
        mp.cancel_upload()
        copy_succeed = False
    return copy_succeed

# private api. Make sure s3_key is valid and unique
def copy_file_to_s3(s3_bucket_object, local_file_path, s3_key):
    logger.info("begin to copy %s to s3 %s" % (local_file_path, s3_key))
    copy_succeed = False
    local_file_size = os.stat(local_file_path).st_size
    run_time = 0
    while run_time < 3 and copy_succeed == False:
      run_time += 1
      try:
          if local_file_size < s3_chunk_size:
              copy_succeed = copy_to_s3_simple(s3_bucket_object, local_file_path, s3_key, local_file_size)
          else:
              copy_succeed = copy_to_s3_parallel(s3_bucket_object, local_file_path, s3_key, local_file_size)
      except Exception as e:
          logger.error("fail to copy file '%s' runtime:%s" % (local_file_path, run_time))
          logger.error("get exception %s" % e)
          logger.error("sleep 10 seconds and retry.")
          time.sleep(10)
          copy_succeed = False
    return copy_succeed

def init_bucket(region, bucket_name):
  s3_conn = boto.s3.connect_to_region(region)
  bucket = s3_conn.get_bucket(bucket_name)
  return bucket

def get_local_heap_dumps(local_root_dir):
  heap_dump_file_pattern = "%s/spark.worker.*.heap.bin" % local_root_dir
  files = glob.glob(heap_dump_file_pattern)
  return files

def get_local_gc_logs(local_root_dir):
  gc_log_file_parttern = "%s/spark.executor.*.gc.log" % local_root_dir
  files = glob.glob(gc_log_file_parttern)
  return files

def get_s3_heap_dumps_file_names(s3_bucket_object):
  s3_heap_dumps = list(s3_bucket_object.list(s3_heap_dump_key_prefix))
  file_names = [ k.name.rsplit("/", 1)[-1] for k in s3_heap_dumps ]
  return file_names

def get_s3_gc_logs_file_names(s3_bucket_object):
  s3_gc_logs = list(s3_bucket_object.list(s3_gc_log_key_prefix))
  file_names = [ k.name.rsplit("/", 1)[-1] for k in s3_gc_logs ]
  return file_names

def upload_heap_dump(s3_bucket_object):
  logger.info("begin to upload heap dump!")
  s3_heap_dump_names = get_s3_heap_dumps_file_names(s3_bucket_object)
  local_heap_dumps = get_local_heap_dumps(local_heap_dump_dir)
  for heap_dump in local_heap_dumps:
    name = heap_dump.rsplit("/", 1)[-1]
    if name not in s3_heap_dump_names:
      key_name = s3_heap_dump_key_prefix + name
      succeed = copy_file_to_s3(s3_bucket_object, heap_dump, key_name)
      if succeed == False:
        logger.error("upload file:%s fails." % heap_dump)
    else:
      logger.info("file:%s exists in s3." % name)

def upload_gc_log(s3_bucket_object):
  logger.info("begin to upload gc log!")
  s3_gc_log_names = get_s3_gc_logs_file_names(s3_bucket_object)
  local_gc_logs = get_local_gc_logs(local_gc_log_dir)
  for gc_log in local_gc_logs:
    name = gc_log.rsplit("/", 1)[-1]
    if name not in s3_gc_log_names:
      key_name = s3_gc_log_key_prefix + name
      succeed = copy_file_to_s3(s3_bucket_object, gc_log, key_name)
      if succeed == False:
        logger.error("upload file:%s fails." % gc_log)
    else:
      logger.info("file:%s exists in s3." % name)

def do_main():
  bucket = init_bucket(s3_aws_region, s3_bucket_name)
  upload_heap_dump(bucket)
  upload_gc_log(bucket)

# always exit with 0, except get some exceptions
do_main()
