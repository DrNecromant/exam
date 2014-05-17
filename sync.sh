for i in {1..1000}; do python sync.py; t=$[ ( $RANDOM % 300 ) + 300 ]s; echo sleep $t; sleep $t; done
