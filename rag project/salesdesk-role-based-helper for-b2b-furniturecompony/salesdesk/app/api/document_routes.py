from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.repositories.document_repository import DocumentRepository
from app.schemas.document_schema import DocumentUploadResponse
from app.security.dependencies import require_admin
from app.services.document_service import DocumentService
from app.services.ingestion.upload_exceptions import (
    DuplicateDocumentError,
    EmptyFileError,
    FileTooLargeError,
    FileTypeMismatchError,
    MissingFilenameError,
    UnsupportedFileTypeError,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


document_service = DocumentService(
    document_repository=DocumentRepository()
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    document_name: str = Form(...),
    category: str = Form(...),
    product_name: str | None = Form(None),
    allowed_roles: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return await document_service.upload_document(
            db=db,
            file=file,
            document_name=document_name,
            category=category,
            product_name=product_name,
            allowed_roles=allowed_roles,
            current_user=current_user,
        )

    except (
        MissingFilenameError,
        UnsupportedFileTypeError,
        FileTypeMismatchError,
        EmptyFileError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except FileTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc

    except DuplicateDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc