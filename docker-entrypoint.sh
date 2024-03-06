#!/bh/sh

flask db upgrade

exec unicorn --bind 0.0.0.0:80 "app:create_app()"