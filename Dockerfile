FROM python:3.8-slim

COPY . /app

RUN pip install flask 
RUN pip install -U finance-datareader
RUN pip install requests
RUN pip install jsonify
RUN pip install pandas
RUN pip install bs4
RUN pip install CORS
RUN pip install flask_cors

WORKDIR /app

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]