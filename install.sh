#!/bin/bash

# Install tukey portal!

# Use the last stable Horizon commit
STABLE=true

# Last commit of Horizon tested against
HORIZON_COMMIT=3a9b0da489030eaacc6cc0416f92192b74783ac8

git clone https://github.com/openstack/horizon.git $HORIZON_DIR

if $STABLE
then
    echo "Using current stable Horizon commit: $HORIZON_COMMIT"
    git checkout $HORIZON_COMMIT
else
    echo "WARNING! Using unstable latest version of Horizon"
fi

# Copy tukey subdir into Horizon 
cp -r $TUKEY_DIR $HORIZON_DIR

cd $HORIZON_DIR

# Apply patches for the stuff we couldn't monkey-patch
patch -p1 < tukey/patches/horizon.patch
patch -p1 < tukey/patches/openstack_dashboard.patch

echo "# Tukey Requirements Added by install.sh 
python-openid
django-openid-auth
psycopg2
python-memcached
" >> tools/pip-requires
