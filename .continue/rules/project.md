# Project Overview

This is a Python project without a framework. It is a combination of Python
tools, Docker configuration, and shell scripts.

## Structure

### Docker

The docker-compose.yml file contains definitions for Crafty Controller, HAProxy,
and the log watcher/listener.

### Shell

This repository is meant to be part of a Minecraft server deployment. As such,
it has scripts to run updates for mods as well as reset the Fetchr Bingo
directory.

### Python

Tox handles the code quality and testing.

There are two main packages and one utility package.

The listener is what watches logs and is the main script of the listener
container. There are multiple ways to listen to a log file, so the various
options are all part of the package, though only one is used.

The updater is a single Python file that updates the server mods. Users should
have a mod_updates.json file in their Minecraft config directory that is similar
to the mod_updates.json.example file. The mod_slugs.json file maps mod slugs to
their respective mod IDs on Modrinth.

Utilities are used by both packages.

If it makes sense, these three packages (or even independent utilities) could
be split into separate repositories as libraries.

To make things more specific per package, each package contains its own
requirements.txt file, which are all aggregated by the root requirements.txt.

## Coding Standards

- Follow PEP8
- Write docstrings
- Use type hints
- Handle exceptions explicitly
- Maximum line length is 79 characters

## Patterns Used

- Variable names should be clear and concise. Use full words as found in a
  dictionary. One word is typically enough.
- Function names should start with a verb and clearly indicate what they do.

## Testing

Tests should go in the tests directory next to the src directory.
Organize tests into files that correspond to the package they test.

Use pytest for unit tests, not unittest.
Unit tests should be pure unit tests without any external dependencies.
Use mocks in unit tests when necessary.
Consider mutation testing when writing unit tests.
Consider writing integration tests when writing tests that require external
dependencies.

## Repository

The project lives at /Users/mts7/Repositories/minecraft-server-runtime
When using git tools, always set the working directory to this path first.
