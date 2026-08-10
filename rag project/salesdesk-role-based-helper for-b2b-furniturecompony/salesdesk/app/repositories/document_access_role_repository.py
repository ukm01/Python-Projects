from sqlalchemy.orm import Session

from app.models.document_access_role_model import DocumentAccessRole
from app.models.document_model import Document, DocumentStatus


class DocumentAccessRoleRepository:

    def list_roles(
        self,
        db: Session,
        document_id: int,
    ) -> list[str]:
        rows = (
            db.query(DocumentAccessRole.role)
            .filter(DocumentAccessRole.document_id == document_id)
            .order_by(DocumentAccessRole.role)
            .all()
        )
        return [row.role for row in rows]

    def list_accessible_document_ids(
        self,
        db: Session,
        role: str,
    ) -> list[int]:
        rows = (
            db.query(Document.id)
            .join(
                DocumentAccessRole,
                DocumentAccessRole.document_id == Document.id,
            )
            .filter(
                DocumentAccessRole.role == role,
                Document.status == DocumentStatus.READY,
            )
            .order_by(Document.id)
            .all()
        )
        return [row.id for row in rows]

    def replace_roles(
        self,
        db: Session,
        document_id: int,
        roles: list[str],
    ) -> None:
        (
            db.query(DocumentAccessRole)
            .filter(DocumentAccessRole.document_id == document_id)
            .delete(synchronize_session=False)
        )
        db.add_all(
            [
                DocumentAccessRole(
                    document_id=document_id,
                    role=role,
                )
                for role in roles
            ]
        )
        db.flush()
