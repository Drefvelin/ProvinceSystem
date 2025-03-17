# Use an official Node.js image
FROM node:18-alpine

# Set working directory
WORKDIR /app/frontend

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the entire project
COPY . .

# Expose Next.js default port
EXPOSE 3000

# Start Next.js
CMD ["npm", "run", "dev"]