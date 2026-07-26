from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.constants.document_categories import DocumentCategory
from app.database import get_db
from app.models.user_model import User
from app.repositories.document_repository import DocumentRepository
from app.schemas.document_schema import (
    DocumentListItemResponse,
    DocumentUploadResponse,
)
from app.security.dependencies import get_current_user, require_admin
from app.services.document_service import DocumentService
from app.services.ingestion.upload_exceptions import (
    DocumentBusyError,
    DuplicateDocumentError,
    EmptyFileError,
    FileTooLargeError,
    FileTypeMismatchError,
    InvalidDocumentRolesError,
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


@router.get(
    "",
    response_model=list[DocumentListItemResponse],
)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return document_service.list_documents(db)


@router.get("/categories")
def get_document_categories(
    current_user: User = Depends(get_current_user),
):
    return {
        "categories": [
            category.value
            for category in DocumentCategory
        ]
    }


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    document_name: str = Form(...),
    category: DocumentCategory = Form(...),
    product_name: str | None = Form(None),
    allowed_roles: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        queued_document = await document_service.queue_document_upload(
            db=db,
            file=file,
            document_name=document_name,
            category=category.value,
            product_name=product_name,
            allowed_roles=allowed_roles,
            current_user=current_user,
        )
        background_tasks.add_task(
            document_service.process_document,
            queued_document.document.id,
            queued_document.replacement,
        )
        return queued_document.document

    except (
        MissingFilenameError,
        UnsupportedFileTypeError,
        FileTypeMismatchError,
        EmptyFileError,
        InvalidDocumentRolesError,
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

    except (
        DuplicateDocumentError,
        DocumentBusyError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    document_service.delete_document(
        db=db,
        document_id=document_id,
    )
