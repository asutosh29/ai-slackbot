from enum import Enum
from typing import List, Optional, Required

try:
    # Use modern typing features if available (Python 3.11+)
    from typing import TypedDict, NotRequired
except ImportError:
    # Fallback for older Python versions
    from typing_extensions import TypedDict, NotRequired

# --- Enumerations for Controlled Vocabularies ---

class ArchiveFormat(Enum):
    """
    Enumeration for the available archive formats for retrieval.
    Maps friendly names to the numeric codes required by the API.
    
    Attributes:
        PNG (int): Represents the PNG image format (code 0).
        JPEG (int): Represents the JPEG image format (code 1).
        PDF (int): Represents the PDF document format (code 2).
        READABILITY_JSON (int): Represents the Readability JSON format (code 3).
        MONOLITH_HTML (int): Represents the Monolith HTML format (code 4).
    """
    PNG = 0
    JPEG = 1
    PDF = 2
    READABILITY_JSON = 3
    MONOLITH_HTML = 4

class ArchiveUploadFormat(Enum):
    """
    Enumeration for the supported archive formats for upload.
    This is a subset of ArchiveFormat as per the OpenAPI specification.
    
    Attributes:
        PNG (int): Represents the PNG image format (code 0).
        JPEG (int): Represents the JPEG image format (code 1).
        PDF (int): Represents the PDF document format (code 2).
    """
    PNG = 0
    JPEG = 1
    PDF = 2

# --- API Resource Models ---

class Tag(TypedDict):
    """Represents a tag resource returned by the API."""
    id: int
    name: str
    ownerId: int
    createdAt: str
    updatedAt: str

class Collection(TypedDict):
    """Represents a collection resource returned by the API."""
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    parentId: Optional[int]
    isPublic: bool
    ownerId: int
    createdAt: str
    updatedAt: str

class Link(TypedDict):
    """Represents a link resource returned by the API."""
    id: str
    url: str
    name: str
    description: Optional[str]
    image: Optional[str]
    imageBlur: Optional[str]
    domain: str
    pinned: bool
    isPublic: bool
    ownerId: int
    collectionId: Optional[int]
    createdAt: str
    updatedAt: str
    tags: List

class Token(TypedDict):
    """Represents an API token resource returned by the API."""
    id: int
    name: str
    isSession: bool
    expires: Optional[str]
    createdAt: str

class User(TypedDict):
    """Represents a user profile resource returned by the API."""
    id: int
    username: str
    email: str
    avatar: Optional[str]
    createdAt: str

# --- Request Payload Models ---

class CreateLinkPayloadTag(TypedDict):
    """
    Structure for a tag when creating a new link.
    
    Fields:
        name (str): The name of the tag to associate.
    """
    id: Optional[int]
    name: List[str]

class CreateLinkPayloadCollection(TypedDict):
    """
    Sub Payload Collection structure for creating a new link via the API.
    
    Fields:
        id (int): collection id to save into (required).
        name (NotRequired[Optional[str]]): (Optional) A custom name/title for the link.
    """
    id: Required[int]
    name: NotRequired[str]

class CreateLinkPayload(TypedDict):
    """
    Payload structure for creating a new link via the API.
    
    Fields:
        url (str): The URL to save (required).
        name (NotRequired[Optional[str]]): A custom name/title for the link.
        description (NotRequired[Optional[str]]): A custom description.
        collection (NotRequired[Optional[CreateLinkPayloadCollection]]): The collection to add this link to.
        tags (NotRequired]): A list of tags to associate.
    """
    url: str
    name: NotRequired[Optional[str]]
    description: NotRequired[Optional[str]]
    collection: NotRequired[Optional[CreateLinkPayloadCollection]]
    tags: NotRequired[Tag]

class UpdateLinkPayloadTag(TypedDict):
    """
    Structure for a tag when creating a new link.
    
    Fields:
        name (str): The name of the tag to associate.
    """
    id: Optional[int]
    name: Required[List[str]]
    
class UpdateLinkPayloadCollection(TypedDict):
    """
    Sub Payload Collection structure for creating a new link via the API.
    
    Fields:
        id: Required[int]: collection id to save into (required).
        ownerId: Required[int]: (Optional) owner id of the collection.
    """
    id: Required[int]
    ownerId: Required[int]

class UpdateLinkPayload(TypedDict):
    """
    Payload structure for updating an existing link.
    
    Fields:
    
        id (Required[int]): Link Id of the link to Update. It is "id" and not "link_id"
        url (NotRequired[str]): The new URL for the link.
        name (NotRequired[Optional[str]]): The new name/title for the link.
        description (NotRequired[Optional[str]]): The new description for the link.
        collection: Required[Optional[UpdateLinkPayloadCollection]]: The new collection params for the link.
        tags: Required[List[UpdateLinkPayloadTag]]: Tags detail
        pinnedBy: Required[List[Optional[int]]]: The new pinned status for the link.
    """
    id: Required[int]
    url: NotRequired[str]
    name: NotRequired[Optional[str]]
    description: NotRequired[Optional[str]]
    collection: Required[UpdateLinkPayloadCollection]
    tags: Required[List[UpdateLinkPayloadTag]] # List of tag names
    pinnedBy: Required[List[Optional[int]]]

class CreateCollectionPayload(TypedDict):
    """
    Payload structure for creating a new collection.
    
    Fields:
        name (str): The name of the collection (required).
        description (NotRequired[Optional[str]]): A description for the collection.
        icon (NotRequired[Optional[str]]): An icon name for the collection.
        color (NotRequired[Optional[str]]): A hex color code for the collection.
        parentId (NotRequired[Optional[int]]): The ID of a parent collection.
    """
    name: str
    description: NotRequired[Optional[str]]
    icon: NotRequired[Optional[str]]
    color: NotRequired[Optional[str]]
    parentId: NotRequired[Optional[int]]

class UpdateCollectionPayload(TypedDict):
    """
    Payload structure for updating an existing collection.
    
    Fields:
        name (NotRequired[str]): The new name for the collection.
        description (NotRequired[Optional[str]]): The new description for the collection.
        icon (NotRequired[Optional[str]]): The new icon name for the collection.
        color (NotRequired[Optional[str]]): The new hex color code for the collection.
        parentId (NotRequired[Optional[int]]): The new parent collection ID.
    """
    name: NotRequired[str]
    description: NotRequired[Optional[str]]
    icon: NotRequired[Optional[str]]
    color: NotRequired[Optional[str]]
    parentId: NotRequired[Optional[int]]

class CreateTagPayload(TypedDict):
    """
    Payload structure for creating a new tag.
    
    Fields:
        name (str): The name of the tag to create (required).
    """
    name: str

class CreateTokenPayload(TypedDict):
    """
    Payload structure for creating a new API token.
    
    Fields:
        name (str): A descriptive name for the token (required).
        expires (NotRequired[int]): The token's lifetime in days. 0 means no expiry.
    """
    name: str
    expires: NotRequired[int]