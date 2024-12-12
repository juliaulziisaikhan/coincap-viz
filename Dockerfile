# base image with python
FROM python:3.12-slim

# set working directory
WORKDIR /app

# copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy all app code
COPY . .

# expose the port streamlit uses
EXPOSE 8501

# command to run the app
CMD ["sh", "-c", "streamlit run market_summary.py --server.port=$PORT --server.address=0.0.0.0"]
