#!/bin/bash
# Starts the practice shop, runs every lesson and saves the real output as NN_name.out.
cd "$(dirname "$0")"
python3 shop_server.py 2>/dev/null & server=$!
sleep 1
L="locust --headless --only-summary --loglevel WARNING --host http://127.0.0.1:8765"
$L -f 02_tasks.py -u 4 -r 4 -t 6s 2>&1 | grep '^tasks run' > 02_tasks.out
for c in ConstantUser RandomUser PacedUser; do
  $L -f 02_waits.py $c -u 1 -r 1 -t 6s 2>&1 | grep 'ran its task'
done > 02_waits.out
$L -f 03_users.py -u 8 -r 8 -t 4s 2>&1 | grep '^users spawned\|^buyer' > 03_users.out
$L -f 04_lifecycle.py -u 2 -r 2 -t 3s 2>&1 | grep 'TEST\|on_start\|on_stop\|task ' > 04_lifecycle.out
$L -f 05_http.py -u 5 -r 5 -t 8s 2>&1 | grep -v '^$' | awk '/^Response time percentiles/{skip=1} !skip' > 05_http.out
$L -f 06_validate.py -u 4 -r 4 -t 8s 2>&1 | grep -v '^$' | awk '/^Response time percentiles/{skip=1} /^Error report/{skip=0} !skip' > 06_validate.out
$L -f 07_shape.py 2>&1 | grep '^step\|Aggregated' | awk '/Aggregated/{n++; if(n>1) next} 1' > 07_shape.out
# distributed: one master, two workers on this computer
LM="locust -f 05_http.py --host http://127.0.0.1:8765"
$LM --worker --loglevel INFO > /dev/null 2>&1 &
$LM --worker --loglevel INFO > /dev/null 2>&1 &
$LM --master --expect-workers 2 --headless --only-summary -u 6 -r 6 -t 8s --loglevel INFO 2>&1 \
  | sed -E 's/^\[[0-9-]+ [0-9:,]+\] [^/]+\/INFO\///; s/^[0-9.]+ ?//; s/Worker '?[A-Za-z0-9.-]+_[0-9a-f]{32}'?/Worker <id>/' | grep -v '^$' | awk '/^Response time percentiles/{skip=1} !skip' > 08_distributed.out
wait $(jobs -p | grep -v $server) 2>/dev/null
kill $server
