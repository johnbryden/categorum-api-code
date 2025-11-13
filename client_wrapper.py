import requests
from typing import Any, Dict, Optional

class JobsApiClient:
    """Convenience wrapper for the Jobs API."""

    def __init__(self, base_url: str, api_key: str, *, default_timeout: int = 30) -> None:
        if not base_url:
            raise ValueError("base_url is required")
        if not api_key:
            raise ValueError("api_key is required")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.default_timeout = default_timeout

    def _build_headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        normalized_path = path if path.startswith("/") else f"/{path}"
        url = f"{self.base_url}{normalized_path}"
        method_upper = method.upper()

        request_headers = self._build_headers(headers)
        effective_timeout = timeout if timeout is not None else self.default_timeout

        print(f"{method_upper} {url}")
        response = requests.request(
            method=method_upper,
            url=url,
            headers=request_headers,
            params=params,
            json=json,
            data=data,
            timeout=effective_timeout,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            error_payload: Any
            try:
                error_payload = response.json()
            except ValueError:
                error_payload = response.text
            raise requests.HTTPError(
                f"{exc} | Response body: {error_payload}",
                response=response,
                request=exc.request,
            ) from None

        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return response.text

    def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        return self.request(
            "GET",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    def post(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        return self.request(
            "POST",
            path,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )


jobs_client: Optional[JobsApiClient] = None