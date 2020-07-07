FROM ubuntu:20.04
LABEL maintainer="JJ Ben-Joseph (jbenjoseph@iqt.org)" \
      description="A coronavirus dashboard container designed for high performance and minimal attack surface."
ARG DEBIAN_FRONTEND=noninteractive
EXPOSE 8080
CMD uwsgi --http :8080 --module corona_dashboard.app:SERVER
COPY setup.py README.rst /app/
COPY corona_dashboard /app/corona_dashboard
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3-minimal python3-pip libopenblas0-openmp cython3 \
      python3-dev build-essential cmake libopenblas-openmp-dev \
      gfortran libffi-dev python3-pkg-resources python3-wheel \
      libpython3.8 \
 && CFLAGS="-g0 -O3 -Wl,--strip-all -I/usr/include:/usr/local/include -L/usr/lib:/usr/local/lib" \
    pip3 install --compile --no-cache-dir --global-option=build_ext \
       --global-option="-j 4" -e .[full] \
 && apt-get remove -y python3-dev python3-pip build-essential cmake \
      libopenblas-openmp-dev gfortran libffi-dev \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/* /tmp/*
