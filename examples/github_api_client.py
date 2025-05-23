#!/usr/bin/env python3
"""
Example of how to create a custom API client using DCApiX.

This example demonstrates how to create a custom API client for a GitHub-like API
by extending the DCApiX classes.
"""

import os
import sys
from pathlib import Path

# Add src directory to path to import dc_api_x
# If the package is installed, you can remove these lines
sys.path.insert(0, Path.resolve(Path(__file__).parent.parent / "src"))


from dc_api_x import ApiClient, ApiResponse, BaseModel, Entity, EntityManager


class GitHubTokenError(ValueError):
    """Exception raised when GitHub token is missing."""

    def __init__(self):
        super().__init__("GitHub token is required")


class GitHubUser(BaseModel):
    """GitHub User model."""

    id: int
    login: str
    name: str | None = None
    bio: str | None = None
    email: str | None = None
    followers: int = 0
    following: int = 0


class GitHubRepo(BaseModel):
    """GitHub Repository model."""

    id: int
    name: str
    description: str | None = None
    owner: GitHubUser
    stars: int = 0
    forks: int = 0
    private: bool = False


class GitHubApiClient(ApiClient):
    """
    Custom GitHub API client.

    This extends the DCApiX ApiClient with GitHub-specific functionality.
    """

    def __init__(
        self,
        token: str | None = None,
        url: str = "https://api.github.com",
        **kwargs,
    ):
        """
        Initialize GitHub API client.

        Args:
            token: GitHub API token
            url: GitHub API URL (default: https://api.github.com)
            **kwargs: Additional arguments for ApiClient
        """
        # GitHub uses token authentication instead of username/password
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise GitHubTokenError()

        # Initialize parent class without username/password
        super().__init__(
            url=url,
            username="token",  # Placeholder, not used
            password="token",  # Placeholder, not used  # noqa: S106
            **kwargs,
        )

        # Override authentication
        self.session.auth = None
        self.session.headers.update(
            {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

        # Initialize entity manager
        self.entities = GitHubEntityManager(self)

    def get_authenticated_user(self) -> ApiResponse:
        """Get the authenticated user."""
        return self.get("user")

    def search_repositories(
        self,
        query: str,
        sort: str | None = None,
        order: str = "desc",
        per_page: int = 30,
        page: int = 1,
    ) -> ApiResponse:
        """
        Search GitHub repositories.

        Args:
            query: Search query
            sort: Sort field (stars, forks, updated)
            order: Sort order (asc, desc)
            per_page: Results per page
            page: Page number

        Returns:
            ApiResponse: Search results
        """
        params = {
            "q": query,
            "per_page": per_page,
            "page": page,
        }

        if sort:
            params["sort"] = sort
            params["order"] = order

        return self.get("search/repositories", params=params)


class GitHubEntityManager(EntityManager):
    """Entity manager for GitHub API."""

    def __init__(self, client: GitHubApiClient):
        """Initialize GitHub entity manager."""
        super().__init__(client)

        # Register built-in entity types
        self._register_entities()

    def _register_entities(self):
        """Register built-in entity types."""
        self.entities["users"] = self.get_entity("users", GitHubUser)
        self.entities["repositories"] = self.get_entity("repos", GitHubRepo)

    def get_user_entity(self) -> Entity:
        """Get users entity."""
        return self.get_entity("users", GitHubUser)

    def get_repository_entity(self) -> Entity:
        """Get repositories entity."""
        return self.get_entity("repos", GitHubRepo)


class GitHubRepository(Entity):
    """GitHub Repository entity with specialized methods."""

    def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
    ) -> ApiResponse:
        """
        Get repository issues.

        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            sort: Sort field (created, updated, comments)
            direction: Sort direction (asc, desc)

        Returns:
            ApiResponse: list of issues
        """
        return self.client.get(
            f"repos/{owner}/{repo}/issues",
            params={
                "state": state,
                "sort": sort,
                "direction": direction,
            },
        )

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        labels: list[str] | None = None,
    ) -> ApiResponse:
        """
        Create an issue in a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            body: Issue body
            labels: Issue labels

        Returns:
            ApiResponse: Created issue
        """
        data = {
            "title": title,
            "body": body,
        }

        if labels:
            data["labels"] = labels

        return self.client.post(f"repos/{owner}/{repo}/issues", json_data=data)


def main():
    """Run the example."""
    # Create GitHub API client
    try:
        client = GitHubApiClient()
        print("✅ GitHub API client initialized")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Set the GITHUB_TOKEN environment variable and try again.")
        return 1

    # Get authenticated user
    user_response = client.get_authenticated_user()
    if user_response.success:
        user = user_response.data
        print(f"👤 Authenticated as: {user['login']} ({user.get('name', 'N/A')})")
    else:
        print(f"❌ Authentication failed: {user_response.error}")
        return 1

    # Search for repositories
    search_response = client.search_repositories("python api client", sort="stars")
    if search_response.success:
        items = search_response.data.get("items", [])
        total = search_response.data.get("total_count", 0)
        print(f"🔍 Found {total} repositories")

        # Print top repositories
        for i, repo in enumerate(items[:5], 1):
            print(f"  {i}. {repo['full_name']} - ⭐ {repo['stargazers_count']}")
            print(f"     {repo['description']}")
    else:
        print(f"❌ Search failed: {search_response.error}")

    # Using entity API
    repos = client.entities.get_repository_entity()

    # Get a repository
    repo_response = repos.get("octocat/Hello-World")
    if repo_response.success:
        repo = repo_response.data
        print(f"\n📦 Repository: {repo['full_name']}")
        print(f"   Description: {repo['description']}")
        print(f"   Stars: {repo['stargazers_count']}")
        print(f"   Forks: {repo['forks_count']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
