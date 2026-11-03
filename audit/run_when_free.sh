#!/usr/bin/env bash
# Start a command only when the machine has at least $MIN_FREE_MB of free physical memory,
# checking every 5 minutes, then run it once at below-normal priority.
# usage: MIN_FREE_MB=2500 audit/run_when_free.sh <log> <command...>
set -u
MIN_FREE_MB=${MIN_FREE_MB:-2500}
log=$1; shift
free_mb() { powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1KB)"; }
while true; do
  f=$(free_mb | tr -d '\r')
  echo "$(date '+%F %T') free=${f}MB" >> "$log.wait"
  if [ "${f:-0}" -ge "$MIN_FREE_MB" ]; then break; fi
  sleep 300
done
echo "$(date '+%F %T') starting" >> "$log.wait"
"$@" > "$log" 2>&1 &
pid=$!
sleep 5
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | ? CommandLine -match 'extract_dvs' | % { (Get-Process -Id \$_.ProcessId).PriorityClass='BelowNormal' }" >/dev/null 2>&1
wait $pid
echo "$(date '+%F %T') finished rc=$?" >> "$log.wait"
