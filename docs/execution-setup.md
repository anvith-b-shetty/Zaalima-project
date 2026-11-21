
# Code Executor - Environment Setup

## Project
Autonomous Multimodal Scientific Discovery Agent

## Assigned Role
Member 3 - Code Executor

## Development Environment

- Operating System: Windows 11
- Python Version: 3.12.10
- Virtual Environment: .venv
- Container Runtime: Docker Desktop
- Docker Image: python:3.12-slim
- Code Editor: Visual Studio Code
- Version Control: Git

## Required Applications

1. Visual Studio Code
2. Python 3.12
3. Git
4. Docker Desktop

## Python Environment Setup

Create the virtual environment:

python -m venv .venv

Install project dependencies:

python -m pip install -r requirements.txt

## Docker Setup

Verify Docker:

docker --version

Test Docker:

docker run hello-world

Download Python execution image:

docker pull python:3.12-slim

## Running the Execution API

Start the API server:

python -m uvicorn src.scientific_discovery.execution.api:app --reload --host 127.0.0.1 --port 8000

## API Documentation

http://127.0.0.1:8000/docs

## Environment Notes

The .venv directory is excluded from GitHub using .gitignore.

Docker is used to execute Python code inside restricted containers.
