FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Generate types from Swagger (optional, can be done manually)
# RUN npm run generate-types || echo "Backend not available, skipping type generation"

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]

