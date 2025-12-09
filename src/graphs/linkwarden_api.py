import requests
from typing import Any, Dict, List, BinaryIO, Optional

from.linkwarden_exceptions import (
    LinkwardenAPIError,
    LinkwardenAuthError,
    LinkwardenNotFoundError,
    LinkwardenServerError,
)
from.linkwarden_types import (
    Collection, CreateCollectionPayload, UpdateCollectionPayload,
    Link, CreateLinkPayload, UpdateLinkPayload,
    Tag, CreateTagPayload,
    Token, CreateTokenPayload,
    User,
    ArchiveFormat, ArchiveUploadFormat
)

class LinkwardenClient:
    """
    A client for interacting with the Linkwarden v1 API.

    This client provides a Pythonic interface to the Linkwarden API,
    handling authentication, request serialization, and error handling.
    It is designed to be a direct implementation of the official
    Linkwarden OpenAPI v1 specification.
    """

    def __init__(self, base_url: str, api_token: str):
        """
        Initializes the Linkwarden API client.

        Args:
            base_url: The base URL of the Linkwarden instance 
                      (e.g., "https://linkwarden.example.com").
            api_token: The API token for authentication.
        
        Raises:
            ValueError: If the base_url is invalid.
        """
        if not base_url or not base_url.startswith(('http://', 'https://')):
            raise ValueError("A valid base_url (starting with http:// or https://) is required.")
        
        if base_url.endswith('/'):
            base_url = base_url[:-1]
            
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json",
            "Content-type":'application/json'
        })

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """
        A centralized helper method to make API requests and handle responses.

        This method intelligently sets the Content-Type header based on whether
        'json' or 'files' are provided in kwargs. It also implements a robust
        error handling strategy, converting HTTP errors into custom exceptions.

        Args:
            method: The HTTP method (e.g., "GET", "POST").
            endpoint: The API endpoint path (e.g., "api/v1/collections").
            **kwargs: Additional arguments to pass to the requests library,
                      such as 'json', 'params', or 'files'.

        Returns:
            The parsed JSON response from the API's "response" key, or raw 
            bytes for direct file downloads.

        Raises:
            LinkwardenAuthError: For 401 or 403 errors.
            LinkwardenNotFoundError: For 404 errors.
            LinkwardenServerError: For 5xx server errors.
            LinkwardenAPIError: For other 4xx client errors or network issues.
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self.session.headers
        
        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()

            try:
                data = response.json()
                return data
            except requests.exceptions.JSONDecodeError:
                if response.ok:
                    return response.content
                raise LinkwardenAPIError(
                    f"Request failed with status {response.status_code}, "
                    f"and the response body was not valid JSON: {response.text}"
                )

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            error_text = e.response.text
            if status_code in (401, 403):
                raise LinkwardenAuthError(f"Authentication error ({status_code}): {error_text}") from e
            elif status_code == 404:
                raise LinkwardenNotFoundError(f"Resource not found ({status_code}): {error_text}") from e
            elif 500 <= status_code < 600:
                raise LinkwardenServerError(f"Server error ({status_code}): {error_text}") from e
            else:
                raise LinkwardenAPIError(f"HTTP client error ({status_code}): {error_text}") from e
        except requests.exceptions.RequestException as e:
            raise LinkwardenAPIError(f"A network request failed: {e}") from e

    # # --- Archives ---
    
    # def get_archive(self, link_id: str, format: ArchiveFormat, preview: bool = False) -> bytes:
    #     """
    #     Retrieves an archive file for a specific link.

    #     Args:
    #         link_id: The ID of the link for which to retrieve the archive.
    #         format: The desired format of the archive, using the ArchiveFormat enum.
    #         preview: Whether to return a preview of the archive. Defaults to False.

    #     Returns:
    #         The raw binary content of the archive file.
    #     """
    #     params = {"format": format.value, "preview": str(preview).lower()}
    #     return self._request("GET", f"api/v1/archives/{link_id}", params=params)

    # def upload_archive(self, link_id: str, format: ArchiveUploadFormat, file: BinaryIO) -> Dict:
    #     """
    #     Uploads an archive file for a specific link.

    #     Args:
    #         link_id: The ID of the link to associate the archive with.
    #         format: The format of the file being uploaded, using the ArchiveUploadFormat enum.
    #         file: A binary file-like object representing the archive to upload.

    #     Returns:
    #         A dictionary containing the API's success response.
    #     """
    #     params = {"format": format.value}
    #     files = {"file": file}
    #     return self._request("POST", f"api/v1/archives/{link_id}", params=params, files=files)

    # --- Collections ---

    def get_collections(self) -> List[Collection]:
        """
        Retrieves a list of all collections for the authenticated user.

        Returns:
            A list of Collection objects.
        """
        return self._request("GET", "api/v1/collections")

    def create_collection(self, payload: CreateCollectionPayload) -> Collection:
        """
        Creates a new collection.

        Args:
            payload: A CreateCollectionPayload object containing the details
                     of the collection to be created.

        Returns:
            The newly created Collection object.
        """
        return self._request("POST", "api/v1/collections", json=payload)

    def get_collection_by_id(self, collection_id: int) -> Collection:
        """
        Retrieves a single collection by its ID.

        Args:
            collection_id: The ID of the collection to retrieve.

        Returns:
            The requested Collection object.
        """
        return self._request("GET", f"api/v1/collections/{collection_id}")

    def update_collection(self, collection_id: int, payload: UpdateCollectionPayload) -> Collection:
        """
        Updates an existing collection.

        Args:
            collection_id: The ID of the collection to update.
            payload: An UpdateCollectionPayload object containing the fields to update.

        Returns:
            The updated Collection object.
        """
        return self._request("PUT", f"api/v1/collections/{collection_id}", json=payload)

    # def delete_collection(self, collection_id: int) -> Dict:
    #     """
    #     Deletes a collection.

    #     Args:
    #         collection_id: The ID of the collection to delete.

    #     Returns:
    #         A dictionary containing the API's success response.
    #     """
    #     return self._request("DELETE", f"api/v1/collections/{collection_id}")

    # --- Links ---

    def get_links(self) -> List[Link]:
        """
        Retrieves a list of all links for the authenticated user.

        Returns:
            A list of Link objects.
        """
        return self._request("GET", "api/v1/links")

    def create_link(self, payload: CreateLinkPayload) -> Link:
        """
        Creates a new link.

        Args:
            payload: A CreateLinkPayload object containing the URL and other
                     details of the link to be created.

        Returns:
            The newly created Link object.
        """
        return self._request("POST", "api/v1/links", json=payload)

    def get_link_by_id(self, link_id: int) -> Link:
        """
        Retrieves a single link by its ID.

        Args:
            link_id: The ID of the link to retrieve.

        Returns:
            The requested Link object.
        """
        return self._request("GET", f"api/v1/links/{link_id}")

    def update_link(self, link_id: int, payload: UpdateLinkPayload) -> Link:
        """
        Updates an existing link.

        Args:
            id: The ID of the link to update.
            payload: An UpdateLinkPayload object containing the fields to update.

        Returns:
            The updated Link object.
        """
        return self._request("PUT", f"api/v1/links/{link_id}", json=payload)

    # def delete_link(self, link_id: int) -> Dict:
    #     """
    #     Deletes a link.

    #     Args:
    #         link_id: The ID of the link to delete.

    #     Returns:
    #         A dictionary containing the API's success response.
    #     """
    #     return self._request("DELETE", f"api/v1/links/{link_id}")

    # --- Tags ---

    def get_tags(self) -> List:
        """
        Retrieves a list of all tags for the authenticated user.

        Returns:
            A list of Tag objects.
        """
        return self._request("GET", "api/v1/tags")

    def create_tag(self, payload: CreateTagPayload) -> Tag:
        """
        Creates a new tag.

        Args:
            payload: A CreateTagPayload object containing the name of the tag.

        Returns:
            The newly created Tag object.
        """
        return self._request("POST", "api/v1/tags", json=payload)

    # # --- Tokens ---

    # def get_tokens(self) -> List:
    #     """
    #     Retrieves a list of all API tokens for the authenticated user.

    #     Returns:
    #         A list of Token objects.
    #     """
    #     return self._request("GET", "api/v1/tokens")

    # def create_token(self, payload: CreateTokenPayload) -> Dict:
    #     """
    #     Creates a new API token. The response contains the new token value,
    #     which should be stored securely as it will not be retrievable again.

    #     Args:
    #         payload: A CreateTokenPayload object with the name and optional
    #                  expiry for the new token.

    #     Returns:
    #         A dictionary containing the details of the new token, including
    #         the 'token' value itself.
    #     """
    #     return self._request("POST", "api/v1/tokens", json=payload)

    # def revoke_token(self, token_id: int) -> Dict:
    #     """
    #     Revokes an existing API token.

    #     Args:
    #         token_id: The ID of the token to revoke.

    #     Returns:
    #         A dictionary containing the API's success response.
    #     """
    #     return self._request("DELETE", f"api/v1/tokens/{token_id}")

    # --- Users ---

    def get_current_user(self) -> User:
        """
        Retrieves the profile of the currently authenticated user.

        Returns:
            A User object representing the current user.
        """
        return self._request("GET", "api/v1/users/me")
    
    # --- Search ---
    def search_query(self, query: str) -> List[Link]:
        """
        Performs an advanced search for links.

        Args:
            query: The search query string, which can include operators
                   like 'tag:', 'collection:', 'before:', etc.

        Returns:
            A List of Link Objects
        """
        return self._request("GET", "api/v1/search",params={"searchQueryString":query})
    