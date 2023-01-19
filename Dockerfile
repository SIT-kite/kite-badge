FROM wamvtan/yolox

COPY ./ /badge

COPY ./nano.py /YOLOX/exps/example/custom/nano.py

WORKDIR /badge

RUN ["pip", "install", "-r", "requirements.txt"]

CMD [ "python3", "main.py" ]