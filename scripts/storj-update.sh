#!/bin/bash

# Exit Codes
############
SUCCESS=0
GENERIC_ERROR=1

# Initial Sanity Checks
#######################
# Currently, only root or members of the docker group can
# run docker commands. This check is needed until that requirement
# is lifted.
in_docker_group=$(grep docker /etc/group | grep -c $USER)
if [[ UID -ne 0 ]] && [[ $in_docker_group -eq 0 ]]; then
  echo "You need to be root or a member of the docker group to run this script."
  exit $GENERIC_ERROR
fi

# Check for required commands
command_list="docker jq"
for c in $command_list; do
  if [[ $(which $c > /dev/null ; echo $?) -ne 0 ]]; then
    echo "$c command not found. Please install it before using this script."
    exit $GENERIC_ERROR
  fi
done

# Main
##############
nodes_path="/etc/storj-utils/nodes.json"

if [[ ! -e $nodes_path ]]; then
  echo "The path does not exist: $nodes_path"
  exit 1
fi

node_names=$(jq -r '.[] | .name' $nodes_path)
run_paths=$(jq -r '.[] | .path + "/run.sh"' $nodes_path)

# Stop and remove the containers for each node.
for n in $node_names; do
  docker stop -t 300 $n && docker rm $n \
    && echo "Successfully stopped and removed $n container." \
    || { echo "Failed to stop and remove $n container. Exiting..." ; exit $GENERIC_ERROR ; }
done

# Pull the update.
docker pull storjlabs/storagenode:latest || echo "Failed to update the storj docker image."

# Start the nodes
for rp in $run_paths; do
  if [[ -e $rp ]]; then
    /bin/bash $rp
  else
    echo "The path does not exist: $rp"
  fi
done

# Count inactive nodes
active_containers=$(docker ps)
inactive_count=0

for n in $node_names; do
  if [[ $(echo "$active_containers" | grep -c $n) -eq 0 ]]; then
    echo "Container for $n is not active."
    ((inactive_count++))
  fi
done

# Finishing
echo -e "Finished with $inactive_count inactive nodes."
exit $SUCCESS
