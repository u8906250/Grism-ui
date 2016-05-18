#!/bin/sh
DEPLOYMENT_PATH=deployment
GRISM_LGUI_PATH=$DEPLOYMENT_PATH/usr/local/grism/lgui
GRISM_LGUI_APP_PATH=$GRISM_LGUI_PATH/applications/Grism
OUTPUT_PATH=grism-lgui.tgz

rm -rf $DEPLOYMENT_PATH
mkdir $DEPLOYMENT_PATH
mkdir -p $GRISM_LGUI_PATH
mkdir -p $GRISM_LGUI_APP_PATH
mkdir -p $GRISM_LGUI_APP_PATH/views
mkdir -p $GRISM_LGUI_APP_PATH/databases

cp web2py/web2py.py $GRISM_LGUI_PATH
cp web2py/welcome.w2p $GRISM_LGUI_PATH
cp web2py/routes.py $GRISM_LGUI_PATH
cp web2py/VERSION $GRISM_LGUI_PATH
cp -R web2py/gluon $GRISM_LGUI_PATH
cp -R web2py/applications/Grism/controllers $GRISM_LGUI_APP_PATH
cp -R web2py/applications/Grism/models $GRISM_LGUI_APP_PATH
cp -R web2py/applications/Grism/static $GRISM_LGUI_APP_PATH
cp -R web2py/applications/Grism/private $GRISM_LGUI_APP_PATH
cp -R web2py/applications/Grism/views/grism $GRISM_LGUI_APP_PATH/views

#cp -R web2py/applications/admin $GRISM_LGUI_PATH/applications
#cp web2py/server.* $GRISM_LGUI_PATH

#set version
echo `git rev-parse --abbrev-ref HEAD |grep -v HEAD || git describe --tags --exact-match` > $GRISM_LGUI_PATH/version
git rev-parse HEAD > $GRISM_LGUI_PATH/revision

tar -C $DEPLOYMENT_PATH/ -zcvf $OUTPUT_PATH .
touch $OUTPUT_PATH.ok

echo build ... done
