# Stage 1: Building the application
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy the frontend code AND the shared directory
COPY frontend/ .
COPY shared/ ./shared

# Build the Next.js application
RUN npm run build

# Stage 2: Production server
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy only the necessary files from the builder
COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Expose the Next.js port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
