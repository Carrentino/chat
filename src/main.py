import uvicorn

from src.bootstrap import make_app  # noqa
from src.settings import get_settings


def main() -> None:
    uvicorn.run(
        # app='main:make_app',
        app=make_app,
        # workers=get_settings().workers_count,
        host=get_settings().host,
        port=get_settings().port,
        # reload=get_settings().reload,
        log_level=get_settings().log_level,
        factory=True,
    )


if __name__ == '__main__':
    main()
