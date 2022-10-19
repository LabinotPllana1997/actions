FROM python:3.8

#download & install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - &&\
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' &&\
    apt-get -y update &&\
    apt-get install -y google-chrome-stable

    


#copy local files
COPY . .

# WORKDIR /file_for_docker
#install dependencies
RUN pip install -r ./requirements.txt
#
ENTRYPOINT ["python", "web_scraper.py"]
