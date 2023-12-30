#!/bin/bash

# Runs the program repeatedly in fully automated mode and checks that it terminates correctly.

NUM_SIMULATIONS=10
GUESSER_WINS=0
LIBRARIAN_WINS=0

for i in $(seq 1 $NUM_SIMULATIONS); do
  echo "===== Running simulation $i ====="
  # Play as the guesser, in fully automated mode
  result=$(python application/main.py <<- EOF | tail -1
	2
	1
	EOF
	)

	if [[ $result == "Guessers win!" ]]; then
	  echo $result
	  GUESSER_WINS=$((GUESSER_WINS+1))
	elif [[ $result == "Librarians win!" ]]; then
	  echo $result
    LIBRARIAN_WINS=$((LIBRARIAN_WINS+1))
  else
    echo "Unexpected result: $result"
    exit 1
  fi
done

echo "===== Results ====="
echo "Guessers won $GUESSER_WINS times"
echo "Librarians won $LIBRARIAN_WINS times"