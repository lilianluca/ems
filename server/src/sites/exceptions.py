from src.core.exceptions import ConflictError, ForbiddenError, NotFoundError


class SiteNotFoundError(NotFoundError):
    """Exception raised when a requested site is not found."""

    def __init__(self, site_id: int):
        super().__init__(
            message=f"Site with ID {site_id} not found",
            code="site_not_found",
        )


class MembershipNotFoundError(NotFoundError):
    """Exception raised when a requested site membership is not found."""

    def __init__(self, membership_id: int):
        super().__init__(
            message=f"Membership with ID {membership_id} not found",
            code="membership_not_found",
        )


class InsufficientSitePermissionsError(ForbiddenError):
    """Exception raised when a user does not have sufficient permissions for a site."""

    def __init__(self):
        super().__init__(
            message="You do not have sufficient permissions for this site",
            code="insufficient_site_permissions",
        )


class UserAlreadyMemberError(ConflictError):
    """Exception raised when a user is already a member of a site."""

    def __init__(self, user_id: int, site_id: int):
        super().__init__(
            message=f"User with ID {user_id} is already a member of site with ID {site_id}",
            code="user_already_member",
        )
