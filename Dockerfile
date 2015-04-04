FROM python
ADD . /project
RUN du -sh /project
WORKDIR /project
RUN pip install -r requirements.txt
EXPOSE 8000
ENTRYPOINT python app.py
