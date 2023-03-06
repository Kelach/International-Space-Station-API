FROM python:3.8.10
RUN pip install Flask==2.2.2
RUN pip install requests==2.28.2
RUN pip install geopy==2.3.0
COPY iss_tracker.py /iss_tracker.py
CMD ["python3", "iss_tracker.py"]