class FileUploadError(Exception):
    """Base exception for file upload errors."""


class MissingFilenameError(FileUploadError):
    pass


class UnsupportedFileTypeError(FileUploadError):
    pass


class FileTypeMismatchError(FileUploadError):
    pass


class FileTooLargeError(FileUploadError):
    pass


class EmptyFileError(FileUploadError):
    pass


class DuplicateDocumentError(FileUploadError):
    pass