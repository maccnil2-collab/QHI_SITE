import hashlib
import os
import re
from collections.abc import AsyncIterable
from pathlib import Path, PurePosixPath
from uuid import uuid4


MAX_DOCUMENT_SIZE = 10 * 1024 * 1024
ALLOWED_DOCUMENT_TYPES = {
    "application/pdf": ("pdf", lambda data: data.startswith(b"%PDF-")),
    "image/jpeg": ("jpg", lambda data: data.startswith(b"\xff\xd8\xff")),
    "image/png": ("png", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
}
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]")


class DocumentValidationError(ValueError):
    pass


def _resolved_root(root: Path) -> Path:
    if not root.is_absolute():
        raise DocumentValidationError("Document storage path must be absolute")
    root_path = root.expanduser().resolve()
    project_root = Path(__file__).resolve().parents[3]
    if root_path == project_root or project_root in root_path.parents:
        raise DocumentValidationError("Document storage must be outside the application repository")
    return root_path


async def read_upload(chunks: AsyncIterable[bytes], max_bytes: int = MAX_DOCUMENT_SIZE) -> bytes:
    content = bytearray()
    async for chunk in chunks:
        if len(content) + len(chunk) > max_bytes:
            raise DocumentValidationError("Document exceeds the upload size limit")
        content.extend(chunk)
    if not content:
        raise DocumentValidationError("Document is empty")
    return bytes(content)


def validate_document(filename: str, content_type: str, content: bytes) -> tuple[str, str]:
    safe_name = _CONTROL_CHARACTERS.sub("", filename.replace("\\", "/").split("/")[-1]).strip()
    if not safe_name or safe_name in {".", ".."}:
        raise DocumentValidationError("A valid filename is required")
    if len(safe_name) > 255:
        raise DocumentValidationError("Filename is too long")
    descriptor = ALLOWED_DOCUMENT_TYPES.get(content_type.lower().split(";", 1)[0].strip())
    if descriptor is None or not descriptor[1](content):
        raise DocumentValidationError("Only valid PDF, JPEG, and PNG documents are accepted")
    return safe_name, descriptor[0]


def store_document(root: Path, order_id: int, filename: str, content_type: str, content: bytes) -> tuple[str, str, str, int]:
    safe_name, extension = validate_document(filename, content_type, content)
    if not content or len(content) > MAX_DOCUMENT_SIZE:
        raise DocumentValidationError("Document exceeds the upload size limit")
    root_path = _resolved_root(root)
    order_dir = root_path / str(order_id)
    order_dir.mkdir(parents=True, exist_ok=True)
    key = f"{order_id}/{uuid4().hex}.{extension}"
    target = (root_path / key).resolve()
    try:
        target.relative_to(root_path)
    except ValueError as error:
        raise DocumentValidationError("Invalid storage key") from error
    try:
        with target.open("xb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
    except OSError:
        target.unlink(missing_ok=True)
        raise
    return key, safe_name, hashlib.sha256(content).hexdigest(), len(content)


def resolve_document(root: Path, storage_key: str) -> Path:
    root_path = _resolved_root(root)
    key_path = PurePosixPath(storage_key)
    if key_path.is_absolute() or len(key_path.parts) != 2 or any(part in {"", ".", ".."} for part in key_path.parts):
        raise DocumentValidationError("Invalid storage key")
    resolved = root_path.joinpath(*key_path.parts).resolve()
    try:
        resolved.relative_to(root_path)
    except ValueError as error:
        raise DocumentValidationError("Invalid storage key") from error
    return resolved
