FROM node:18

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

RUN python3 -m venv /app/venv

COPY requirements.txt .
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PATH="/app/venv/bin:$PATH"

EXPOSE 8080

CMD ["yarn", "start"]
