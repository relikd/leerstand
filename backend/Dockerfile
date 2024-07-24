FROM python:3.11-alpine

EXPOSE 8000

# install base system
RUN apk add --no-cache gcc libc-dev linux-headers
RUN pip install --upgrade pip
RUN pip install uvicorn gunicorn

# install requirements
WORKDIR /django_project
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# then scripts (likely wont change often)
ENV PATH="/scripts:/py/bin:$PATH"
COPY --chmod=700 ./scripts /scripts

# finally copy app (likely will invalidate cache)
COPY . .

CMD ["run.sh"]
