# --- BUILD STAGE ---
FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# --- RUNTIME STAGE ---
FROM node:22-alpine AS runner
WORKDIR /app

# Create non-root user
RUN adduser -D -H appuser
USER appuser

COPY --from=builder /app ./

EXPOSE 3000

CMD ["npm", "run", "start"]
