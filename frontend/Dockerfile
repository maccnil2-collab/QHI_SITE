FROM node:24-alpine AS dependencies
WORKDIR /app
COPY package.json ./package.json
COPY package-lock.json ./package-lock.json
RUN npm ci

FROM node:24-alpine AS builder
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
COPY --from=dependencies /app/node_modules ./node_modules
COPY . ./
RUN mkdir -p public && npm run typecheck && npm run build

FROM node:24-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0
RUN addgroup --system --gid 10001 qhi \
    && adduser --system --uid 10001 --ingroup qhi --home /app qhi
COPY --from=builder --chown=qhi:qhi /app/public ./public
COPY --from=builder --chown=qhi:qhi /app/.next/standalone ./
COPY --from=builder --chown=qhi:qhi /app/.next/static ./.next/static
USER 10001:10001
EXPOSE 3000
CMD ["node", "server.js"]
