param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("up","down","tests","migrate")]
    [string]$cmd = "up"
)

switch ($cmd) {
    "up" {
        docker compose up -d
    }
    "down" {
        docker compose down -v
    }
    "tests" {
        python -m pytest -q
    }
    "migrate" {
        alembic upgrade head
    }
}
