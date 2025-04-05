FROM python:3.10

WORKDIR /homesecurity

# Copy the rest of your application code into the container
COPY .. .


# Install dependencies from poetry with pip (TODO: Create and use a venv for this instead)
RUN pip3 install -e .
