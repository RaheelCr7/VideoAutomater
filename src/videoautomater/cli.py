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


@app.command("demo")
def demo(
    output: str = typer.Option("output/animation_demo", "--output", "-o", help="Directory for demonstration output"),
):
    """Generate a 20-second cinematic animation proof-of-concept demonstrating the upgraded engine."""
    from videoautomater.orchestration.demo_runner import AnimationDemoRunner

    console.print(
        Panel.fit(
            f"[bold cyan]VideoAutomater v{__version__} // Explanatory Animation Engine[/bold cyan]\n"
            f"[dim]Rendering 20-second Cinematic Motion & Subtitle Quality Proof-of-Concept...[/dim]",
            border_style="cyan",
        )
    )

    runner = AnimationDemoRunner(output_dir=Path(output))
    with console.status("[bold green]Rendering cinematic animations & word-aligned subtitles...", spinner="dots"):
        demo_path = asyncio.run(runner.run_demonstration())

    console.print(
        Panel.fit(
            f"[bold green]Animation Demonstration Rendered Successfully![/bold green]\n"
            f"[bold]Video:[/bold] {demo_path}\n"
            f"[bold]Contact Sheet:[/bold] {demo_path.parent / 'contact_sheet.jpg'}\n"
            f"[bold]Artifacts:[/bold] {demo_path.parent}",
            border_style="green",
        )
    )


@app.command("test-10s")
def test_10s(
    output: str = typer.Option("output/ten_second_test", "--output", "-o", help="Directory for 10-second quality test output"),
):
    """Generate the 10-second Beyond 80 visual-first cinematic quality test."""
    from videoautomater.orchestration.ten_second_runner import TenSecondTestRunner

    console.print(
        Panel.fit(
            f"[bold cyan]Beyond 80 // Cinematic Visual-First Quality Test[/bold cyan]\n"
            f"[dim]Executing 10-second Hybrid Documentary & 3D Simulation Production...[/dim]",
            border_style="cyan",
        )
    )

    runner = TenSecondTestRunner(output_dir=Path(output))
    with console.status("[bold green]Rendering cinematic motion & word-aligned subtitles...", spinner="dots"):
        test_path = asyncio.run(runner.run_quality_test())

    console.print(
        Panel.fit(
            f"[bold green]Beyond 80 10-Second Quality Test Completed Successfully![/bold green]\n"
            f"[bold]Video:[/bold] {test_path}\n"
            f"[bold]Contact Sheet:[/bold] {test_path.parent / 'contact_sheet.jpg'}\n"
            f"[bold]Artifacts:[/bold] {test_path.parent}",
            border_style="green",
        )
    )


@app.command("pilot")
def pilot(
    output: str = typer.Option("output/episode_001", "--output", "-o", help="Directory for 80-second pilot output"),
    force: bool = typer.Option(False, "--force", "-f", help="Force fresh regeneration of all clips and master video"),
):
    """Generate the complete 80-second Beyond 80 master pilot episode."""
    from videoautomater.orchestration.pilot_runner import PilotRunner

    console.print(
        Panel.fit(
            f"[bold cyan]Beyond 80 // Master Pilot Production (80 Seconds)[/bold cyan]\n"
            f"[dim]Producing Episode 001: The Secret Inside the Ice Giants...[/dim]",
            border_style="cyan",
        )
    )

    runner = PilotRunner(output_dir=Path(output))
    with console.status("[bold green]Executing full 80-second documentary production workflow...", spinner="dots"):
        pilot_path = asyncio.run(runner.run_full_pilot(force_regenerate=force))

    console.print(
        Panel.fit(
            f"[bold green]Beyond 80 Pilot Rendered Successfully![/bold green]\n"
            f"[bold]Master Video:[/bold] {pilot_path}\n"
            f"[bold]Contact Sheet:[/bold] {pilot_path.parent / 'pilot_contact_sheet.jpg'}\n"
            f"[bold]Quality Report:[/bold] {pilot_path.parent / 'quality_report.json'}\n"
            f"[bold]Timeline Report:[/bold] {pilot_path.parent / 'animation_timeline.json'}\n"
            f"[bold]Licensing Manifest:[/bold] {pilot_path.parent / 'asset_licensing_manifest.json'}",
            border_style="green",
        )
    )


def main():
    app()


if __name__ == "__main__":
    main()
