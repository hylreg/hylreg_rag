def cli():
    """Console entrypoint for interactive CLI."""
    from src.cli.cli_interface import main

    main()


def demo():
    """Console entrypoint for demo mode."""
    from src.core.demo import run_demo

    run_demo()


def api():
    """Console entrypoint for API server."""
    import uvicorn

    uvicorn.run("src.api.api_server:app", host="0.0.0.0", port=8000)
