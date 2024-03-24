#!/bin/bash

# Set an initial counter value
counter=2000

# Define the maximum value for the counter
max_count=56000


# Loop while the counter is less than the maximum value
while [ $counter -le $max_count ]
do
    echo "Counter: $counter"
    scrapy crawl articles -O articles_$counter.json -a tag=$counter
    ((counter += 500))
done