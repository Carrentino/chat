set windows-shell := ["pwsh.exe", "-c"]
set dotenv-filename := ".env"

export PYTHONPATH := "src"

remove := if "$(expr substr $(uname -s) 1 5)" == "Linux" { "rm -rf" } else { "rmdir" }

poetry-export:
    poetry export  --without-hashes -f requirements.txt -o requirements.txt

pre-commit-all:
    pre-commit run --all-files --show-diff-on-failure

alembic-gen:
    alembic revision --autogenerate

alembic-upg:
    alembic upgrade head

alembic-drop:
    alembic downgrade base
