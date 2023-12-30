#!/bin/bash

# Runs the program repeatedly in fully automated mode and checks that it terminates correctly.

NUM_SIMULATIONS=$1
GUESSER_WINS_COUNT=0
LIBRARIAN_WINS_COUNT=0
TOTAL_NUM_ATTEMPTS=0

for i in $(seq 1 $NUM_SIMULATIONS); do
  echo "===== Running simulation $i ====="
  # Play as the guesser, in fully automated mode
  result=$(python application/main.py <<- EOF | tail -2
	2
	1
	EOF
	)

  GUESSER_WINS=$(echo $result | grep -o "Guessers win!")
  LIBRARIAN_WINS=$(echo $result | grep -o "Librarians win!")
  NUM_ATTEMPTS=$(echo $result | cut -d'#' -f2 | cut -d'.' -f1)
  echo "Number of attempts: $NUM_ATTEMPTS"


	if [[ -n $GUESSER_WINS ]]; then
	  echo "$GUESSER_WINS"
	  GUESSER_WINS_COUNT=$((GUESSER_WINS_COUNT+1))
	elif [[ -n $LIBRARIAN_WINS ]]; then
	  echo "$LIBRARIAN_WINS"
    LIBRARIAN_WINS_COUNT=$((LIBRARIAN_WINS_COUNT+1))
  else
    echo "Unexpected result: $result"
    exit 1
  fi

  TOTAL_NUM_ATTEMPTS=$((TOTAL_NUM_ATTEMPTS+NUM_ATTEMPTS))
done

echo "===== Results ====="
echo "Guessers won $GUESSER_WINS_COUNT times"
echo "Librarians won $LIBRARIAN_WINS_COUNT times"
echo "AVERAGE_NUM_ATTEMPTS: $(python -c "print($TOTAL_NUM_ATTEMPTS/$NUM_SIMULATIONS)")"