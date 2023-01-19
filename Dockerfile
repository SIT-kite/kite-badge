FROM wamvtan/yolox

COPY ./ /badge

WORKDIR /badge

RUN ["pip", "install", "-r", "requirements.txt"]

CMD [ "python3", "main.py" ]