# Process Environment Variables Viewer

Python script for pretty-printing the environment variables for one or more processes.

## Requirements

- Python 3
- [psutil library](https://pypi.org/project/psutil/)

## Setup

Ensure you have Python 3 installed:

```sh
python3 --version
```

Install the `psutil` package:

```sh
pip3 install psutil
```

## Install

The easiest way to use this script is install it to a location on your path `$PATH`, e.g. `/usr/local/bin` (`sudo` or admin access may be required):

```sh
curl -sLf --retry 3 --tlsv1.2 --proto '=https' 'https://raw.githubusercontent.com/DopplerUniversity/process-env-vars/main/process-env-vars.py' | sudo tee /usr/local/bin/process-env-vars &>/dev/null
sudo chmod +x /usr/local/bin/process-env-vars
```

Then test by running:

```sh
process-env-vars --help
```

## Filtering and matching rules

- All process name-based filters are case sensitive
- All arguments except `--json` support multiple instances, e.g. `--pid 58327 --pid 58325`
- Using `--pid`, `--name` (or a mix of both) short-circuits `--filter` and `--ignore`
- Using `--username` takes precedence over all other filters

## Usage

Note:

- Some processes require `sudo` or admin access to fetch their environment variables
- Zombie processes do not return environment variables

Below are the most common usage examples for finding and filtering the process list:

Filter by user:

```sh
process-env-vars --user rb
```

Match using process ID:

```sh
process-env-vars --pid 58325
```

Match using multiple processes by ID:

```sh
process-env-vars --pid 58327 --pid 58325
```

Filter with exact match for process name:

```sh
process-env-vars --name Figma
```

Filter by exact process name:

```sh
process-env-vars --name figma_agent
```

Find processes where process name contains the supplied value:

```sh
process-env-vars --filter figma
```

Find processes where process name contains either of the supplied values:

```sh
process-env-vars --filter Figma --filter figma
```

Ignore processes where process name contains the supplied value:

```sh
process-env-vars --ignore Chrome
```

Ignore processes where process name contains either of the supplied values:

```sh
process-env-vars --ignore Chrome --ignore Electron
```

Output to JSON format:

```sh
process-env-vars --filter Electron --json
```
