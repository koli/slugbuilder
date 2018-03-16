FROM heroku/heroku:16-build

RUN mkdir /app
RUN addgroup --quiet --gid 2000 slug && \
  useradd slug --uid=2000 --gid=2000 --home-dir /app --no-create-home

ADD . /
RUN chmod +x /bin/*
ENV PYTHONPATH $PYTHONPATH:/usr/local/lib/python3/site-packages
RUN chown -R slug:slug /app
RUN chown slug:slug /bin/read_procfile_keys

USER slug
ENV HOME /app
RUN /builder/install-buildpacks

ENTRYPOINT ["/bin/sh", "-c", "/builder/build.sh"]
