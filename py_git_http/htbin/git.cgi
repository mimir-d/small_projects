#!/bin/sh

GIT_PROJECT_ROOT=`pwd`/htbin/repos GIT_HTTP_EXPORT_ALL=1 git http-backend "$@"
