# APIs/UserAPI.py

from .BaseAPI import BaseAPI


class UserAPI(BaseAPI):
    """
    Wrapper for the User endpoint:

        GET /api/user
    """

    def get_user_info(self, api_token: str):
        """
        Get information about the current API user (subscription, usage, limits).

        Parameters
        ----------
        api_token : str
            Your EODHD API token.

        Returns
        -------
        dict
            User information including subscription details and API usage.
        """
        return self._rest_get_method(
            api_key=api_token,
            endpoint="user",
        )
