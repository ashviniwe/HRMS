# Build stage
FROM node:22-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies using npm install instead of npm ci
RUN npm install

# Copy application code
COPY . .

# Build arguments for environment variables
ARG VITE_CLIENT_ID
ARG VITE_ORG_BASE_URL

ENV VITE_CLIENT_ID=${VITE_CLIENT_ID}
ENV VITE_ORG_BASE_URL=${VITE_ORG_BASE_URL}

# Build the application
RUN npm run build

# Production stage
FROM node:22-alpine

WORKDIR /app

# Install serve to run the production build
RUN npm install -g serve

# Copy built assets from builder stage
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 3000

# Start the application
CMD ["serve", "-s", "dist", "-l", "3000"]
