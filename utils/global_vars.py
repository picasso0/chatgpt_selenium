
from os import getenv
# MINIO Config
MINIO_PROTOCOL="https"
MINIO_URL="minio.sirafgroup.com"
MINIO_ACCESS_KEY="7qMlPjxSnrQ6fKGCPpl3"
MINIO_SECRET_KEY="zuf+RJCJY2rlmuU3WYI7ztbyvnKqq4N7bIdt1AumjA82"
MINIO_BUCKET_NAME="chatgpt"

# MONGODB Config
MONGODB_URL="mongodb://77.238.108.86:27000/log?retryWrites=true&w=majority"

# AUTH Config
AUTH_JWT_SECRET_KEY = "django-insecure-e-8z0#u67o-p@h6muvch)rl5p(01e^-=o*m02x&+t+fq$(3a#^"
AUTH_JWTALGORITHM = "HS256"


# # RABBITMQ Config
# rabbit_host = str(getenv("RABBITMQ_URL"))
# rabbit_port = int(getenv("RABBITMQ_PORT"))
# rabbit_username = str(getenv("RABBITMQ_USERNAME"))
# rabbit_vhost = str(getenv("RABBITMQ_VHOST"))
# rabbit_password = str(getenv("RABBITMQ_PASSWORD"))
# rabbit_exchange = str(getenv("RABBITMQ_EXCHANGE"))
# rabbit_queue = "default"
# rabbit_virasty_routing_key = str(getenv("RABBITMQ_VIRASTY_ROUTING_KEY"))
# rabbit_twitter_routing_key = str(getenv("RABBITMQ_TWITTER_ROUTING_KEY"))
# rabbit_connection = None
# rabbit_channel = None

rabbit_host = "31.214.171.201"
rabbit_port = 5672
rabbit_username = 'gateway'
rabbit_vhost = 'gateway'
rabbit_password = 'Bgateway@1256'
rabbit_exchange = ''
rabbit_queue = 'chatgpt_selenium'
rabbit_promt_routing_key = 'promt'
rabbit_twitter_routing_key = 'answer'
rabbit_connection = None
rabbit_channel = None
