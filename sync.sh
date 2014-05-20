for i in {1..1000}; do python sync.py -t 10; t=$[ ( $RANDOM % 600 ) + 300 ]s; echo sleep $t; sleep $t; done
