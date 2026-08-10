# --- BUILD STAGE ---
# Build context must be ProvinceSystem root (see docker-compose*.yml)
# so ../shared/skins constants resolve (import → /shared/...).
FROM node:22-alpine AS builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
COPY shared /shared

# Baked into the Next client bundle at build time
ARG NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build


# --- RUNTIME STAGE ---
FROM node:22-alpine AS runner

WORKDIR /app

# Create non-root user WITH home directory
RUN adduser -D appuser \
    && mkdir -p /home/appuser/.npm \
    && chown -R appuser:appuser /home/appuser

ENV HOME=/home/appuser

# Copy only what we need
COPY --from=builder /app/package.json /app/package-lock.json ./
RUN npm ci

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.* ./

USER appuser

EXPOSE 3000
CMD ["npm", "run", "start"]
