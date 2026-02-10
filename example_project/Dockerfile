FROM python:3.13

WORKDIR /app

# Copy requirements from root
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy entire project
COPY . /app/

# Install the package in editable mode
RUN pip install -e .
