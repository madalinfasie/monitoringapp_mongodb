FROM python:3.10-slim-bullseye

LABEL maintainer="Madalin Fasie"

ARG CODE=/code

# Make base folder for the source code
RUN mkdir ${CODE}

# Install the required libraries
RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    libssl-dev \
    libpq-dev

# Copy local code to container location and change working dir to that directory
COPY . ${CODE}
WORKDIR ${CODE}

# Install the python packages
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expose the port
EXPOSE 5000

# Default command for the image (this can be overwritten on compose)
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000", "--workers", "3"]