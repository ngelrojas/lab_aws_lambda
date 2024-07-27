# Use Amazon Linux 2 as the base image
FROM amazonlinux:2

# Install necessary packages including OpenSSL development libraries
RUN yum update -y && \
    yum install -y \
    gcc \
    openssl-devel \
    bzip2-devel \
    libffi-devel \
    zlib-devel \
    wget \
    make \
    tar \
    gzip

# Install Python 3.8 and pip
RUN amazon-linux-extras install -y python3.8

# Set Python 3.8 as the default Python version
RUN ln -sf /usr/bin/python3.8 /usr/bin/python

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip3.8 install --upgrade pip
RUN pip3.8 install -r requirements.txt

# Copy the rest of the application code
COPY src/ /app/
COPY tests/ /app/tests/

# Set the entrypoint for the container
ENTRYPOINT ["python", "lambda_function.py"]