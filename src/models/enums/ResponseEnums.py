from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDATION_SUCCESS = "file validated successfully"
    FILE_TYPE_NOT_SUPPORTED = "file type not supported"
    FILE_SIZE_EXCEEDED = "file size exceeds the limit"
    FILE_UPLOAD_SUCCESS = "file upload successfully"
    FILE_UPLOAD_FAILED = "file upload failed"
    FILE_PROCESSING_SUCCESS = "file processed successfully"
    FILE_PROCESSING_FAILED = "file processing failed"
    PROCESSING_SUCCESS = "processing_success"
    PROCESSING_FAILED = "processing_failed"
    NO_FILES_ERROR = "no files founded"
    FILE_ID_ERROR = "no_file_found_with_this_id"
    