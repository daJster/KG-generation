# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /KG-generation

# Copy the local code to the container
COPY . /KG-generation

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Define environment variable
ENV NAME KG-Gen

# Run app.py when the container launches
CMD ["python3", "src/web-app/home/app.py"]