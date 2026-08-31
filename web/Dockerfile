FROM python
WORKDIR /home/myapp
COPY ./templates/* /home/myapp/templates/
COPY ./static/* /home/myapp/static/
COPY ./sample_app.py /home/myapp/
COPY ./requ /home/myapp/
RUN pip install -r requ
CMD ["python", "/home/myapp/sample_app.py"]
EXPOSE 8080
