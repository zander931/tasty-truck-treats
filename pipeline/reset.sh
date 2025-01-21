source .env
mysql -u $DB_USER -p$DB_PASSWORD -h $DB_HOST -P $DB_PORT $DB_NAME -f $1