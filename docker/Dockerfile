FROM python:3.10

WORKDIR /homesecurity

# Create folder in the container used for storing the images (mounted to /images outside of the container)
RUN mkdir /images
# Copy the rest of your application code into the container
COPY .. .


# Install dependencies from poetry with pip (TODO: Create and use a venv for this instead)
RUN pip3 install -e .
