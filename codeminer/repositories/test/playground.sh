mkdir -p /tmp/playground/cvs/server/test_repository
mkdir -p /tmp/playground/cvs/client
cd  /tmp/playground/cvs/server
export CVSROOT=/tmp/playground/cvs/server/
cvs init
cd /tmp/playground/cvs/client
cvs checkout test_repository