# Builds a Docker image to run docker-uwsgi-odis.  The base image will handle
# adding any application files and required dependencies to this image.
#
FROM lzalewsk/flask-uwsgi
MAINTAINER luka <lzalewsk@gmail.com>

# Create a symlink with a unique name to the Flask app's static resources.
# This volume can then get mounted and used by another container.
RUN ln -s /var/www/app/static /var/www/odis-static
VOLUME /var/www/odis-static

# Set default ENV
ENV RABBITMQ_HOST somerabbithost
ENV RABBITMQ_PORT 5672
ENV VIRTUAL_HOST somevhost
ENV USER guest
ENV PASSWD guest
ENV QUEUE somequeue

# Expose the port where uWSGI will run
EXPOSE 5000

# If running this app behind a webserver using the uwsgi protocol (like nginx),
# then use --socket.  Otherwise run with --http to run as a full http server.
#CMD ["uwsgi", "--http", ":5000",         "--wsgi-file", "odis.py", "--callable", "app", "--processes",  "2", "--threads", "4"]
CMD ["uwsgi", "--socket", "0.0.0.0:5000", "--wsgi-file", "odis.py", "--callable", "app", "--processes",  "2", "--threads", "4"]
