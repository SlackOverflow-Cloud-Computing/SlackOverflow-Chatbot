# The base image for python. There are countless official images.
# Alpine just sounded cool.
#
FROM python:3.12

# The directory in the container where the app will run.
#
WORKDIR /code

# Copy the requirements.txt file from the project directory into the working
# directory and install the requirements.
#
COPY ./requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt

# Copy over the files.
#
COPY . /code/.

# Expose/publish port 5002 for the container.
#
EXPOSE 8000

# Look in the code. This is an environment variable
# passed to the application.
#
ENV WHEREAMI=DOCKER

# Run the app.
CMD ["python", "-m", "app.main"]

