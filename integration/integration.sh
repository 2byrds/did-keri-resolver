#!/bin/bash

#
# Run this script from the base SignifyPy directory, like
# signifypy% ./integration/app/delegate.sh
#

#print commands
#set -x

#save this current directory, this is where the integration_clienting file also is
ORIG_CUR_DIR=$( pwd )

KERI_PRIMARY_STORAGE="/usr/local/var/keri"
KERI_FALLBACK_STORAGE="${HOME}/.keri"

KERI_DEV_BRANCH="development"
# KERI_DEV_TAG="c3a6fc455b5fac194aa9c264e48ea2c52328d4c5"
VLEI_DEV_BRANCH="dev"
WEBS_DEV_BRANCH="main"

# OUTPUT_FILE="output.txt"

prompt="y"
function intro() {
    echo "Welcome to the integration script for keri based did methods"
    read -p "Enable prompts?, [y]: " enablePrompts
    prompt=${enablePrompts:-"y"}
    if [ "${prompt}" != "n" ]; then
        echo "Prompts enabled"
    else
        echo "Skipping prompts, using defaults"
    fi
}

function getKeripyDir() {
    # Check if the environment variable is set
    if [ -z "$KERIPY_DIR" ]; then
        default_value="../keripy"
        # Prompt the user for input with a default value
        if [ "${prompt}" == "y" ]; then
            read -p "Set keripy dir [${default_value}]: " keriDirInput
        fi
        # Set the value to the user input or the default value
        KERIPY_DIR=${keriDirInput:-$default_value}
    fi
    # Use the value of the environment variable
    echo "$KERIPY_DIR"
}

function getVleiDir() {
    # Check if the environment variable is set
    if [ -z "$VLEI_DIR" ]; then
        default_value="../vLEI"
        # Prompt the user for input with a default value
        if [ "${prompt}" == "y" ]; then
            read -p "Set vlei dir [${default_value}]: " vleiDirInput
        fi
        # Set the value to the user input or the default value
        VLEI_DIR=${vleiDirInput:-$default_value}
    fi
    # Use the value of the environment variable
    echo "$VLEI_DIR"
}

function runIssueEcr() {
    cd "${ORIG_CUR_DIR}" || exit
    if [ "${prompt}" == "y" ]; then
        read -p "Run vLEI issue ECR script (n to skip)?, [y]: " runEcr
    fi
    runIssueEcr=${runEcr:-"y"}
    if [ "${runIssueEcr}" == "n" ]; then
        echo "Skipping Issue ECR script"
    else
        echo "Running issue ECR script"
        scriptsDir="scripts"
        if [ -d "${scriptsDir}" ]; then
            echo "Launching Issue ECR script"
            cd ${scriptsDir} || exit
            source env.sh
            source issue-ecr.sh
            echo "Completed issue ECR script"
        fi
    fi
    cd "${ORIG_CUR_DIR}" || exit
}

function runWitnessNetwork() {
    cd ${ORIG_CUR_DIR} || exit
    witPid=-1
    keriDir=$(getKeripyDir)
    echo "Keripy dir set to: ${keriDir}"
    if [ "${prompt}" == "y" ]; then
        read -p "Run witness network (y/n)? [y]: " runWitNet
    fi
    runWit=${runWitNet:-"y"}
    if [ "${runWit}" == "y" ]; then
        if [ -d  "${keriDir}" ]; then
            #run a clean witness network
            echo "Launching a clean witness network"
            cd "${keriDir}" || exit
            updateFromGit ${KERI_DEV_BRANCH}
            installPythonUpdates "keri"
            rm -rf ${KERI_PRIMARY_STORAGE}/*;rm -Rf ${KERI_FALLBACK_STORAGE}/*;kli witness demo &
            witPid=$!
            sleep 5
            echo "Clean witness network launched"
        else
            echo "KERIPY dir missing ${keriDir}"
            exit 1
        fi
    else
        echo "Skipping witness network"
    fi
    echo ""
}

function runVlei() {
    # run vLEI cloud agent
    cd ${ORIG_CUR_DIR} || exit
    vleiPid=-1
    if [ "${prompt}" == "y" ]; then
        read -p "Run vLEI (y/n)? [y]: " runVleiInput
    fi
    runVlei=${runVleiInput:-"y"}
    if [ "${runVlei}" == "y" ]; then
        echo "Running vLEI server"
        vleiDir=$(getVleiDir)
        if [ -d "${vleiDir}" ]; then
            cd "${vleiDir}" || exit
            updateFromGit ${VLEI_DEV_BRANCH}
            installPythonUpdates "vlei"
            vLEI-server -s ./schema/acdc -c ./samples/acdc/ -o ./samples/oobis/ &
            vleiPid=$!
            sleep 5
            echo "vLEI server is running"
        else
            echo "vLEI dir missing ${vleiDir}"
        fi
    fi
    echo ""
}

websPid=-1
function runDidWebs() {
    # run did webs 
    cd ${ORIG_CUR_DIR} || exit
    if [ "${prompt}" == "y" ]; then
        read -p "Run did webs (y/n)? [y]: " runWebsInput
    fi
    runWebs=${runWebsInput:-"y"}
    if [ "${runWebs}" == "y" ]; then
        echo "Running did:webs scenario"
        updateFromGit ${WEBS_DEV_BRANCH}
        installPythonUpdates "did:webs"
        dkr did web start --config-dir=./scripts --config-file=dkr.json --http 7776 &
        websPid=$!
        sleep 3
        echo "did:webs service running"
    fi
    echo ""
}

function installPythonUpdates() {
    name=$1
    if [ "${prompt}" == "y" ]; then
        read -p "Install $name?, [n]: " installInput
    fi
    install=${installInput:-"n"}
    if [ "${install}" == "n" ]; then
        echo "Skipping install of $name"
    else
        echo "Installing python module updates..."
        python -m pip install -e .
    fi
}

function updateFromGit() {
    branch=$1
    commit=$2

    if [ "${prompt}" == "y" ]; then
        read -p "Update git repo ${branch} ${commit}?, [n]: " upGitInput
    fi
    update=${upGitInput:-"n"}
    if [ "${update}" == "y" ]; then
        echo "Updating git branch ${branch} ${commit}"
        fetch=$(git fetch)
        echo "git fetch status ${fetch}"
        if [ -z "${commit}" ]; then
            switch=$(git switch "${branch}")
            echo "git switch status ${switch}"
            pull=$(git pull)
            echo "git pull status ${pull}"
        else
            switch=$(git checkout "${commit}")
            echo "git checkout commit status ${switch}"
        fi
    else
        echo "Skipping git update ${branch}"
    fi
}

runAnother="y"
while [ "${runAnother}" != "n" ]
do
    touch "${OUTPUT_FILE}"

    intro

    echo "Setting up services"

    runWitnessNetwork

    set -x
    runIssueEcr
    unset -x

    runDidWebs

    # sleep 3

    # runVlei

    # sleep 3

    # runKeria

    # sleep 3

    # runSignifyIntegrationTests

    # sleep 3

    # runIssueEcr

    echo ""

    read -p "Everything is setup, your services are still running, hit enter to tear down... " teardown
    
    echo "Tearing down any leftover processes"
    #tear down the signify client
    kill "$websPid" >/dev/null 2>&1
    # # tear down the keria cloud agent
    # kill $keriaPid >/dev/null 2>&1
    # # tear down the delegator
    # kill "$delPid" >/dev/null 2>&1
    # # tear down the vLEI server
    # kill $vleiPid >/dev/null 2>&1
    # # tear down the witness network
    kill $witPid >/dev/null 2>&1

    read -p "Run another scenario [n]?: " runAgain
    runAnother=${runAgain:-"n"}
done

function checkServers() {
    read -p "Check server ports to verify cleanup?, [y]: " checkServInput
    if [ "${checkServInput}" == "y" ]; then
        echo "If a server is running you will see a line with the port number"
        echo "Checking witness servers"
        sudo lsof -i -P | grep LISTEN | grep :$PORT | grep -i 563
        echo "Checking did:webs servers"
        sudo lsof -i -P | grep LISTEN | grep :$PORT | grep -i 7776
        # echo "Checking vLEI servers"
        # sudo lsof -i -P | grep LISTEN | grep :$PORT | grep -i 7723
    fi
}

checkServers

echo "Done"