#!/bin/bash
# @Author: Guodong Wang
# @Date:   2015-01-21 16:50:02
# @Last Modified by:   Guodong Wang
# @Last Modified time: 2015-01-22 17:20:31

function usage()
{
	echo "usage: $0 remote-server remote-path"
}

remote_svr=$1
remote_path=$2

if [[ "x$remote_svr" == "x" || "x$remote_svr" == "x-h" ]]
then
	usage
	exit 1
fi

if [[ "x$remote_path" == "x" ]]
then
	# the default dir is in $HOME
	remote_path="code"
fi

local_root_dir=$(cd $(dirname $0); pwd)

rsync -arvz --exclude='.git*' --exclude "*pyc" $local_root_dir $remote_svr:$remote_path

