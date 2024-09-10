import os
from decouple import config

os.environ.setdefault(
    "DATABASE_URL", "postgres://u04dpx4dcly:LMZGoqSquSwO@ep-gentle-mountain-a23bxz6h-pooler.eu-central-1.aws.neon.tech/shell_giver_flip_797988")
os.environ.setdefault("SECRET_KEY", "Monster0483")

# Cloudinary configuration

os.environ.setdefault("CLOUDINARY_CLOUD_NAME", "dpecpzapk")
os.environ.setdefault("CLOUDINARY_API_KEY", "214731326451677")
os.environ.setdefault("CLOUDINARY_API_SECRET", "NhMuqGxD5wG6OMZTe3pbvrgkiQU")

