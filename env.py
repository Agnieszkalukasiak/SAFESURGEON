import os
from decouple import config
os.environ.setdefault(
    "DATABASE_URL", "postgresql://neondb_owner:npg_vgxA9SDyo5Bk@ep-long-lake-a43nbjsx-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require")


# Cloudinary configuration
os.environ.setdefault("SECRET_KEY", "Monster0483")
os.environ.setdefault("CLOUDINARY_CLOUD_NAME", "dpecpzapk")
os.environ.setdefault("CLOUDINARY_API_KEY", "214731326451677")
os.environ.setdefault("CLOUDINARY_API_SECRET", "NhMuqGxD5wG6OMZTe3pbvrgkiQU")

