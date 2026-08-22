ARG NODE_VERSION=24

# ---------- base ----------
FROM node:${NODE_VERSION}-alpine AS base
WORKDIR /app

# ---------- dependencies ----------
FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci

# ---------- development ----------
FROM base AS dev
ARG USER_UID=1000
ARG USER_GID=1000

# The node image ships with uid/gid 1000; remap it when the host differs
# so bind-mounted files are not created as root.
RUN if [ "$USER_UID" != "1000" ] || [ "$USER_GID" != "1000" ]; then \
    deluser node && \
    addgroup -g "$USER_GID" node && \
    adduser -u "$USER_UID" -G node -s /bin/sh -D node; \
    fi

COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN chown -R node:node /app

USER node
EXPOSE 5173
CMD ["npm", "run", "dev"]

# ---------- build ----------
FROM deps AS build
COPY . .
RUN npm run build

# ---------- production ----------
FROM nginx:alpine AS production
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]