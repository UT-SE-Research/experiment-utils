#!/bin/bash

GROUP_ID="edu.illinois"
ARTIFACT_ID="nondex-maven-plugin"
ARTIFACT_VERSION="1.1.2"

if [[ $1 == "" ]]; then
    echo "arg1 - the path to the project, where high-level pom.xml is"
    echo "arg2 - (Optional) Group ID for plugin. Default is $GROUP_ID"
    echo "arg3 - (Optional) Artifact ID for plugin. Default is $ARTIFACT_ID"
    echo "arg4 - (Optional) Artifact version for plugin. Default is $ARTIFACT_VERSION"
    exit
fi

if [[ ! $2 == "" ]]; then
    GROUP_ID=$2
fi

if [[ ! $3 == "" ]]; then
    ARTIFACT_ID=$3
fi

if [[ ! $4 == "" ]]; then
    ARTIFACT_VERSION=$4
fi

crnt=`pwd`
working_dir=`dirname $0`
project_path=$1

cd ${project_path}
project_path=`pwd`
cd - > /dev/null

cd ${working_dir}

javac PomFile.java
find ${project_path} -name pom.xml | grep -v "src/" | java PomFile ${GROUP_ID} ${ARTIFACT_ID} ${ARTIFACT_VERSION}
rm -f PomFile.class

cd ${crnt}
