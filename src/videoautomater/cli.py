"""Command Line Interface for VideoAutomater."""

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from videoautomater import __version__
from videoautomater.orchestration.workflow import ProductionOrchestrator

app = typer.Typer(
    name="videoautomater",
    help="Autonomous AI-Powered Video Creation & Multi-Platform Publishing System",
    add_completion=False,
)
console = Console()


@app.callback()
def main_callback():
    """VideoAutomater: Autonomous AI Video Creation & Multi-Platform Publishing System."""
    pass


@app.command("generate")
def generate(
    duration: float = typer.Option(80.0, "--duration", "-d", help="Target video duration in seconds (default: 80.0)"),
    topic: str = typer.Option("auto", "--topic", "-t", help="Topic query or 'auto' for autonomous discovery"),
    output: str = typer.Option("output", "--output", "-o", help="Root directory for episode output"),
):
    """Generate a complete 80-second broadcast master vertical video with all episode artifacts."""
    console.print(
        Panel.fit(
            f"[bold cyan]VideoAutomater v{__version__}[/bold cyan]\n"
            f"[dim]Autonomous Production Pipeline // Target: {duration}s // Mode: {topic}[/dim]",
            border_style="cyan",
        )
    )

    orchestrator = ProductionOrchestrator(output_root=Path(output))

    with console.status("[bold green]Executing multi-agent production workflow...", spinner="dots"):
        video_path, quality_report = asyncio.run(
            orchestrator.generate_episode(duration=duration, topic=topic)
        )

    # Display Quality Gate Table
    table = Table(title="[bold]Editorial & Technical Quality Verification[/bold]")
    table.add_column("Check", style="cyan")
    table.add_column("Required", style="dim")
    table.add_column("Measured", style="bold")
    table.add_column("Status")

    for chk in quality_report.checks:
        status_color = "green" if chk.status == "PASS" else "red"
        table.add_row(
            chk.check_name,
            chk.required,
            chk.measured,
            f"[{status_color}]{chk.status}[/{status_color}]",
        )

    console.print(table)

    summary_color = "green" if quality_report.passed_all_mandatory_checks else "yellow"
    console.print(
        Panel.fit(
            f"[{summary_color}]Master Video Generated Successfully![/{summary_color}]\n"
            f"[bold]Path:[/bold] {video_path}\n"
            f"[bold]Artifacts Directory:[/bold] {video_path.parent}\n"
            f"[bold]Passed All Quality Gates:[/bold] {quality_report.passed_all_mandatory_checks}",
            border_style=summary_color,
        )
    )


def main():
    app()


if __name__ == "__main__":
    main()
