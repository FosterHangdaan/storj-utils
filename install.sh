#!/bin/bash

# Initial Sanity Checks
#######################
# Check user
if [[ $UID -ne 0 ]]; then
  echo 'You must be root to run this program.'
  exit 1
fi

# Check required commands
required_commands="pip3 realpath dirname"
for c in $required_commands; do
  if [[ $(which $c > /dev/null ; echo $?) -ne 0 ]]; then
    echo "$c command not found. Please install it before using this script."
    exit 1
  fi
done

# Functions
#######################
return_handle() {
  success_msg=${2:-Done}
  fail_msg=${3:-Failed}

  if [[ $1 -eq 0 ]]; then
    echo $success_msg
    return 0
  else
    echo $fail_msg
    exit 0
  fi
}

# Main
#######################
work_dir=$(dirname $(realpath $0))
scripts_dest='/usr/local/bin'
nagios_scripts_dest='/usr/lib/nagios/plugins'
package_dest='/usr/local/lib/python3.8/dist-packages/storjutils'
config_dest='/etc/storj-utils'
nagios_scripts=$(ls -1 ${work_dir}/nagios-plugins/*)
scripts=$(ls -1 ${work_dir}/scripts/*)

echo -n 'Installing python dependencies... '
pip3 install --requirement ./requirements.txt 1>/dev/null 2>&1 ; return_handle $?

if [[ ! -d $package_dest ]]; then
  echo -n 'Creating package directory... '
  mkdir -p $package_dest ; return_handle $?
fi
echo -n 'Copying custom python package... '
rm -rf $package_dest/* && cp ${work_dir}/package/* $package_dest ; return_handle $?

echo -n 'Copying scripts... '
for s in $scripts; do
  filename=$(basename $s)
  filename="${filename%.*}"
  cp $s ${scripts_dest}/$filename
done
echo 'Done'

echo -n 'Copying nagios scripts... '
if [[ -d $nagios_scripts_dest ]]; then
  for ns in $nagios_scripts; do
    filename=$(basename $ns)
    filename="${filename%.*}"
    cp $ns ${nagios_scripts_dest}/$filename \
      && ln -s ${nagios_scripts_dest}/$filename ${scripts_dest}/$filename
  done
else
  for ns in $nagios_scripts; do
    filename=$(basename $ns)
    filename="${filename%.*}"
    cp $ns ${scripts_dest}/$filename
  done
fi
echo 'Done'

if [[ ! -d $config_dest ]] ; then
  echo -n 'Creating config directory... '
  mkdir $config_dest ; return_handle $?
fi
if [[ ! -e ${config_dest}/nodes.json ]]; then
  echo -n Installing nodes configuration file...
  cp ${work_dir}/config/nodes.json $config_dest ; return_handle $?
fi

echo 'Installation Complete.'
exit 0
