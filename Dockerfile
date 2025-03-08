# Use official Node.js image with Python installed
FROM node:18

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

# Create a virtual environment
RUN python3 -m venv /app/venv

# Activate virtual environment and install dependencies
COPY requirements.txt .
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy Node.js dependencies
COPY package.json yarn.lock ./
RUN yarn install --production

# Copy the entire project
COPY . .

# Set Python path to use the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Expose port 8080
EXPOSE 8080

# Run the server
CMD ["yarn", "start"]
