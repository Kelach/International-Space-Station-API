FROM python
RUN pip install Flask==2.2.2
RUN pip install requests==2.22.0
COPY iss_tracker.py /iss_tracker.py
CMD ["python3", "iss_tracker.py"]