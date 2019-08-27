#FROM node:10
FROM gcr.io/google_appengine/nodejs

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
COPY package*.json ./
#COPY requirements.txt ./

RUN apt-get update
RUN apt-get install -y python-pip

RUN npm install
RUN pip install gunicorn
#RUN pip install -r requirements.txt
RUN pip install flake8==2.6.2
RUN pip install coverage==4.5.4

# Bundle app source
COPY . .

EXPOSE 5000
EXPOSE 7000

CMD [ "npm", "run", "backend"]
