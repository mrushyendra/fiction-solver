#!/bin/bash
set -e

COMMAND="$1"

if [[ $COMMAND == "build" ]]; then
  echo "===== Building ====="
  docker-compose build
  exit
elif [[ $COMMAND == "start" ]]; then
  echo "===== Starting game up... ====="
  docker-compose run -e PYTHONPATH=. game
  exit
elif [[ $COMMAND == "stop" ]]; then
  echo "===== Killing services forcefully ====="
  docker-compose down
  exit
elif [[ $COMMAND == "test" ]]; then
  echo "===== Running test suite ====="
  docker-compose run --rm game pytest -s
  exit
fi

echo "Usage:"
echo "  run {build|start|stop|test}"
echo "    build - Builds services."
echo "    start - Starts services."
echo "    stop - Force-stops services (in case CTRL+C did not work)."
echo "    test - Runs test suite."