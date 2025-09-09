#!/bin/bash

# Run Django development server
daphne src.asgi:application --port 8001 --bind 0.0.0.0