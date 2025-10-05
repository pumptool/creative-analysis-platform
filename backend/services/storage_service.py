"""
AWS S3 storage service
"""
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
import logging
from pathlib import Path
from typing import Optional
import uuid

from core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing file storage in AWS S3"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.AWS_S3_BUCKET
    
    async def upload_video(self, file: UploadFile, experiment_id: str) -> str:
        """
        Upload video file to S3
        
        Args:
            file: Video file upload
            experiment_id: Experiment ID for organizing files
            
        Returns:
            S3 key of uploaded file
        """
        try:
            # Generate unique filename
            file_extension = Path(file.filename).suffix
            s3_key = f"experiments/{experiment_id}/video{file_extension}"
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket,
                s3_key,
                ExtraArgs={
                    'ContentType': file.content_type or 'video/mp4'
                }
            )
            
            logger.info(f"Video uploaded to S3: {s3_key}")
            return s3_key
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise Exception(f"Failed to upload video: {str(e)}")
    
    async def upload_csv(
        self,
        file: UploadFile,
        experiment_id: str,
        file_type: str
    ) -> str:
        """
        Upload CSV file to S3
        
        Args:
            file: CSV file upload
            experiment_id: Experiment ID
            file_type: Type of CSV (results, comments)
            
        Returns:
            S3 key of uploaded file
        """
        try:
            s3_key = f"experiments/{experiment_id}/{file_type}.csv"
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket,
                s3_key,
                ExtraArgs={
                    'ContentType': 'text/csv'
                }
            )
            
            logger.info(f"CSV uploaded to S3: {s3_key}")
            return s3_key
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise Exception(f"Failed to upload CSV: {str(e)}")
    
    def get_file_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Generate presigned URL for file access
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds
            
        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise Exception(f"Failed to generate file URL: {str(e)}")
    
    def download_file(self, s3_key: str, local_path: str) -> str:
        """
        Download file from S3 to local path
        
        Args:
            s3_key: S3 object key
            local_path: Local file path
            
        Returns:
            Local file path
        """
        try:
            self.s3_client.download_file(
                self.bucket,
                s3_key,
                local_path
            )
            
            logger.info(f"File downloaded from S3: {s3_key} -> {local_path}")
            return local_path
            
        except ClientError as e:
            logger.error(f"S3 download failed: {e}")
            raise Exception(f"Failed to download file: {str(e)}")
    
    def delete_file(self, s3_key: str) -> None:
        """
        Delete file from S3
        
        Args:
            s3_key: S3 object key
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=s3_key
            )
            
            logger.info(f"File deleted from S3: {s3_key}")
            
        except ClientError as e:
            logger.error(f"S3 deletion failed: {e}")
            raise Exception(f"Failed to delete file: {str(e)}")
