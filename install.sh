#!/bin/bash

# Install tukey portal
# TODO: Write this in python and make it portable


# USER SETTINGS -----
# Site specific installation variables

# Local settings file contains passwords for db etc
LOCAL_SETTINGS_FILE=/var/www/tukey/config/portal/local_settings.py

# Use the last stable Horizon commit
STABLE=true

# run as /something on a domain
MULTI_SITE=false

# create a postgres database for the django/osdc stuff
CREATE_DATABASE=true

# create apache sites-available file
CONFIGURE_APACHE=true

# create main site console.conf apache sites-available file
CREATE_CONSOLE=true

# Where to install MUST be absolute path for linking
BASE_DIR=/var/www/tukey

# directory under BASE_DIR to clone Horizon repo to
HORIZON_DIR=tukey-portal

# user to run apache wsgi as
RUN_USER=ubuntu

# group to run apache wsgi as
RUN_GROUP=ubuntu

# END USER SETTINGS ---

DB_USER="osdcdb_user"
DB_NAME="osdcdb"
DB_PASSWORD="password"

OSDCQUERY_REPO=http://git.bionimbus.org/git/public/osdcquery.git
# Probably wont change
TUKEY_DIR=tukey

# Last commit of Horizon tested against
HORIZON_COMMIT=3a9b0da489030eaacc6cc0416f92192b74783ac8

sudo apt-get install -y nodejs

sudo git clone https://github.com/openstack/horizon.git $BASE_DIR/$HORIZON_DIR
sudo chown -R $RUN_USER:$RUN_GROUP $BASE_DIR/$HORIZON_DIR

if $STABLE
then
    cd $BASE_DIR/$HORIZON_DIR
    echo "Using current stable Horizon commit: $HORIZON_COMMIT"
    sudo git checkout $HORIZON_COMMIT
    cd -
else
    echo "WARNING! Using unstable latest version of Horizon"
fi

# Copy tukey subdir into Horizon 
sudo ln -s $(pwd)/$TUKEY_DIR $BASE_DIR/$HORIZON_DIR

sudo ln -s $LOCAL_SETTINGS_FILE $BASE_DIR/$HORIZON_DIR/openstack_dashboard/local/local_settings.py

cd $BASE_DIR/$HORIZON_DIR

# Apply patches for the stuff we couldn't monkey-patch
sudo patch -p1 < $TUKEY_DIR/patches/horizon.patch
sudo patch -p1 < $TUKEY_DIR/patches/openstack_dashboard.patch
sudo patch -p1 < $TUKEY_DIR/patches/cluster.patch

# Append to 

echo "# Tukey Requirements automatically generated by install.sh 
#python-openid
# Supports http_proxy
#python-openid-lac
python-openid
django-openid-auth
psycopg2
python-memcached
django-recaptcha
pyelasticsearch
feedparser
" | sudo tee -a tools/pip-requires > /dev/null

sudo python tools/install_venv.py

for version in Django==1.4.3 django-openstack-auth==1.0.6
do
    sudo $BASE_DIR/$HORIZON_DIR/tools/with_venv.sh pip install $version
done

if $CONFIGURE_APACHE
then
    # Generate Apache config file openstack-dashboard.conf
    
    echo "# Automatically generated by install.sh
    WSGIScriptAlias / $BASE_DIR/$HORIZON_DIR/openstack_dashboard/wsgi/django.wsgi
    
    WSGIDaemonProcess tukey-portal user=$RUN_USER group=$RUN_GROUP python-path=$BASE_DIR/$HORIZON_DIR:$BASE_DIR/$HORIZON_DIR/.venv/lib/python2.7/site-packages
    
    WSGIProcessGroup tukey-portal
    
    Alias /static $BASE_DIR/$HORIZON_DIR/$TUKEY_DIR/static/
    Alias /misc $BASE_DIR/config/misc/
    
    <Directory $BASE_DIR/$HORIZON_DIR/openstack_dashboard/wsgi>
      <IfModule mod_shib>
        AuthType shibboleth
        ShibRequireSession Off
        ShibUseHeaders On
        require shibboleth
      </IfModule>

      Order allow,deny
      Allow from all
    </Directory>

    <Directory $BASE_DIR/$HORIZON_DIR/$TUKEY_DIR/static>
      Order allow,deny
      Allow from all
    </Directory>

    <Directory $BASE_DIR/config/misc>
      Order allow,deny
      Allow from all
    </Directory>" | sudo tee $TUKEY_DIR/openstack-dashboard.conf > /dev/null
    
    sudo ln -s $BASE_DIR/$HORIZON_DIR/$TUKEY_DIR/openstack-dashboard.conf /etc/apache2/sites-available/
    

    if $CREATE_CONSOLE
    then    
    
        echo "# Automatically generated by install.sh
        NameVirtualHost *:80
        
        
        <Virtualhost *:80>
            ServerName console.opensciencedatacloud.org
        
            ErrorLog /var/log/apache2/console-error.log
            CustomLog /var/log/apache2/console-access.log common
        
            UseCanonicalName On
        
            include /etc/apache2/sites-available/openstack-dashboard.conf
        
        </virtualhost>" | sudo tee /etc/apache2/sites-available/console > /dev/null

        sudo a2ensite console

    fi

fi

if $CREATE_DATABASE
then
    if [ -z $DB_NAME ] || [ -z $DB_USER ] || [ -z $DB_PASSWORD ]
    then
        echo "Variables DB_NAME DB_USER and DB_PASSWORD need to be set"
        exit 1
    else
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
        sudo -u postgres psql -c "CREATE USER $DB_USER with PASSWORD '$DB_PASSWORD';"
    fi
fi

cd $BASE_DIR/$HORIZON_DIR/$TUKEY_DIR/osdcquery
git clone $OSDCQUERY_REPO
cd osdcquery
git checkout dev

cd $BASE_DIR/$HORIZON_DIR
tools/with_venv.sh python manage.py syncdb
