from django.conf import settings
from storages.backends.s3boto import S3BotoStorage

class MatrixS3BotoStorage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = getattr(settings, 'MATRIX_AWS_STORAGE_BUCKET_NAME')
        super(MatrixS3BotoStorage, self).__init__(*args, **kwargs)