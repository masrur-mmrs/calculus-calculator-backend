# Use an official Node.js image
FROM node:18

# Set the working directory
WORKDIR /app

# Copy package.json and yarn.lock first (for caching dependencies)
COPY package.json yarn.lock ./

# Install Node.js dependencies
RUN yarn install --production

# Copy the entire project
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y python3 python3-pip

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port 3001 (or whatever port your Express server uses)
EXPOSE 3001

# Start the server
CMD ["yarn", "start"]
