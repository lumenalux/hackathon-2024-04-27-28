FROM node:20-alpine AS base
WORKDIR /usr/src/app
COPY package*.json ./

FROM base AS dependencies
RUN npm install --only=production
COPY . .


FROM base AS release

COPY --from=dependencies /usr/src/app/node_modules ./node_modules

COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
