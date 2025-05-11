# CrewAI Demo: Trip Planning Assistant

This project is a demonstration of CrewAI's capabilities for building autonomous AI agent systems. It is intended **for example purposes only**.

## Overview

This demo showcases how CrewAI can be used to create a trip planning assistant that:

- Identifies suitable cities to visit in a given country based on the current season
- Collects detailed information about each recommended city
- Creates a comprehensive trip plan with itineraries and recommendations

## Project Structure

- `/crews`: Contains the crew definitions and flow configurations
- `/tools`: Custom tools for the agents to use
- `/utils`: Utility functions including custom logging
- `/logs`: Generated output and logs from crew executions

## Usage

To run the demo:

```bash
python main.py
```

The demo will generate a trip plan for Iran during summer by default, which you can modify in the main.py file.

## Disclaimer

This is a demonstration project only and is meant to showcase the capabilities of CrewAI for building autonomous agent systems. It is not intended for production use.
