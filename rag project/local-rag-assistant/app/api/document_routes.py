from fastapi import APIRouter, UploadFile, File, HTTPException, status

from app.services.document_service import document_service

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    try:
        result = await document_service.upload_and_index_document(file)
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error while uploading document: {str(error)}"
        )