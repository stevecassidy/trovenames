#!/bin/bash
# script to upload a new version of the dataset to 4store

export OS_AUTH_URL=https://keystone.rc.nectar.org.au:5000/v2.0/

# With the addition of Keystone we have standardized on the term **tenant**
# as the entity that owns the resources.
export OS_TENANT_ID=016dec894b7847668f45d564dc4bb476
export OS_TENANT_NAME="HCSvLab"

# In addition to the owning entity (tenant), openstack stores the entity
# performing the action as the **user**.
export OS_USERNAME="steve.cassidy@mq.edu.au"

# With Keystone you pass the keystone password.
export OS_PASSWORD=ZTU5ZGNhMjI5ZWM5NDkw


sudo supervisorctl stop 4store

4s-backend-destroy trove
4s-backend-setup trove

mkdir -p trove-ttl 
cd trove-ttl
for gzf in $(swift list trove-ttl); do
     echo $gzf
     swift download trove-ttl $gzf
     gunzip $gzf

     for f in *.ttl; do
	      echo $f
          4s-import  -v trove --add --model http://trove.alveo.edu.au/ $f
          rm $f
      done

done

sudo supervisorctl start 4store

