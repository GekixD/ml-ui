# Use Node.js (latest stable)
FROM node:20

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose the React development server port
EXPOSE 5173

# Start the development server
CMD ["npm", "run", "dev"]

# Serve React with Nginx
# FROM nginx:latest
# COPY --from=builder /app/build /usr/share/nginx/html
# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]
