"""Generation stack for synthetic therapy dialogue creation.

The GenerationStack orchestrates the interaction between Patient, Router,
and Therapist agents to produce complete IRT therapy sessions.

This stack is used to:
1. Generate synthetic dialogues for training/evaluation
2. Create frozen histories for the evaluation stack
3. Test the full IRT protocol flow
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from src.agents import PatientAgent, RouterAgent, TherapistAgent
from src.core import Conversation, Stage, Message, list_vignettes

logger = logging.getLogger(__name__)
console = Console()


class GenerationStack:
    """Orchestrates full IRT therapy dialogue generation.
    
    The generation stack manages the interaction loop:
    1. Patient speaks (describes nightmare, responds to therapist)
    2. Router determines current stage
    3. Therapist responds based on stage
    4. Repeat until FINAL stage
    
    Attributes:
        patient: The patient simulator agent
        therapist: The therapist agent
        router: The stage router agent
        conversation: The current conversation state
        language: Session language
        max_turns: Maximum number of turns before forced termination
        
    Example:
        >>> stack = GenerationStack.from_vignette("anxious")
        >>> dialogue = await stack.run()
        >>> stack.save_dialogue("dialogues/anxious_001.json")
    """
    
    def __init__(
        self,
        patient: PatientAgent,
        therapist: TherapistAgent | None = None,
        router: RouterAgent | None = None,
        language: str = "en",
        max_turns: int = 50,
        session_id: str | None = None,
    ) -> None:
        """Initialize the generation stack.
        
        Args:
            patient: Configured patient agent with vignette
            therapist: Optional therapist agent (created if not provided)
            router: Optional router agent (created if not provided)
            language: Session language ("en" or "de")
            max_turns: Maximum turns before forced termination
            session_id: Optional session ID (generated if not provided)
        """
        self.patient = patient
        self.therapist = therapist or TherapistAgent(language=language)
        self.router = router or RouterAgent()
        self.language = language
        self.max_turns = max_turns
        
        self.conversation = Conversation(
            session_id=session_id or str(uuid.uuid4()),
            language=language,
        )
        
        self._turn_count = 0
        self._is_complete = False
    
    @classmethod
    def from_vignette(
        cls,
        vignette_name: str,
        language: str = "en",
        max_turns: int = 50,
    ) -> "GenerationStack":
        """Create a generation stack from a vignette name.
        
        Args:
            vignette_name: Name of the vignette file (without .json)
            language: Session language ("en" or "de")
            max_turns: Maximum turns before forced termination
            
        Returns:
            Configured GenerationStack instance
            
        Example:
            >>> stack = GenerationStack.from_vignette("cooperative", language="de")
        """
        patient = PatientAgent.from_vignette(vignette_name, language=language)
        return cls(patient=patient, language=language, max_turns=max_turns)
    
    def _display_message(
        self,
        content: str,
        speaker: str,
        stage: str | None = None,
        turn: int | None = None,
    ) -> None:
        """Display a message with rich formatting.
        
        Args:
            content: Message content
            speaker: Speaker name
            stage: Current stage (optional)
            turn: Turn number (optional)
        """
        # Build title
        title_parts = []
        if turn is not None:
            title_parts.append(f"Turn {turn}")
        title_parts.append(speaker)
        if stage:
            title_parts.append(f"[{stage}]")
        title = " - ".join(title_parts)
        
        # Color by speaker
        if speaker == self.patient.name:
            color = "blue"
        elif speaker == "Therapist":
            color = "green"
        else:
            color = "white"
        
        panel = Panel(
            Text(content, style=color),
            title=title,
            border_style=color,
            padding=(1, 2),
        )
        console.print(panel)
        console.print()
    
    def _display_stage_transition(self, old_stage: str | None, new_stage: str) -> None:
        """Display a stage transition notification."""
        if old_stage != new_stage:
            console.print(
                f"[bold yellow]>>> Stage transition: "
                f"{old_stage or 'START'} → {new_stage}[/bold yellow]"
            )
            console.print()
    
    async def _patient_turn(self, therapist_message: str | None = None) -> str:
        """Execute a patient turn.
        
        Args:
            therapist_message: Previous therapist message (None for initial)
            
        Returns:
            Patient's response content
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task(
                f"[blue]{self.patient.name} is thinking...[/blue]",
                total=None,
            )
            
            if therapist_message is None:
                # Initial message - patient describes nightmare
                response = self.patient.get_initial_message()
                usage = {}
            else:
                # Respond to therapist
                response, usage = await self.patient.generate(
                    user_message=therapist_message,
                    conversation=self.conversation,
                )
        
        return response.strip()
    
    async def _router_turn(self) -> Stage:
        """Execute a router turn to determine stage.
        
        Returns:
            Determined therapy stage
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task(
                "[yellow]Determining stage...[/yellow]",
                total=None,
            )
            
            stage = await self.router.classify_and_update(self.conversation)
        
        return stage
    
    async def _therapist_turn(self, patient_message: str) -> str:
        """Execute a therapist turn.
        
        Args:
            patient_message: Patient's message to respond to
            
        Returns:
            Therapist's response content
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task(
                "[green]Therapist is responding...[/green]",
                total=None,
            )
            
            response, usage = await self.therapist.generate(
                user_message=patient_message,
                conversation=self.conversation,
            )
        
        return response.strip()
    
    async def run(self, verbose: bool = True) -> Conversation:
        """Run the full dialogue generation.
        
        Executes the Patient -> Router -> Therapist loop until
        the FINAL stage is reached or max_turns is exceeded.
        
        Args:
            verbose: Whether to display rich output (default True)
            
        Returns:
            The completed Conversation object
        """
        if verbose:
            console.print(Panel(
                f"Starting IRT dialogue generation\n"
                f"Patient: [blue]{self.patient.name}[/blue] "
                f"({self.patient.vignette_name})\n"
                f"Language: {self.language}\n"
                f"Max turns: {self.max_turns}",
                title="Generation Stack",
                border_style="bold blue",
            ))
            console.print()
        
        # Initialize with intro message context
        intro_message = self.therapist.get_intro_message()
        if verbose:
            self._display_message(intro_message, "Therapist (Intro)", stage="intro")
        
        # Patient starts by describing nightmare
        patient_response = await self._patient_turn(therapist_message=None)
        self.conversation.add_message(patient_response, "user")
        self._turn_count += 1
        
        if verbose:
            self._display_message(
                patient_response,
                self.patient.name,
                turn=self._turn_count,
            )
        
        previous_stage = None
        
        while not self._is_complete and self._turn_count < self.max_turns:
            # Router determines stage
            stage = await self._router_turn()
            
            if verbose:
                self._display_stage_transition(previous_stage, stage.value)
            
            # Update therapist's stage
            self.therapist.update_stage(stage)
            
            # Therapist responds
            therapist_response = await self._therapist_turn(patient_response)
            self.conversation.add_message(
                therapist_response,
                "assistant",
                stage=stage.value,
            )
            self._turn_count += 1
            
            if verbose:
                self._display_message(
                    therapist_response,
                    "Therapist",
                    stage=stage.value,
                    turn=self._turn_count,
                )
            
            # Check for completion
            if stage == Stage.FINAL:
                self._is_complete = True
                break
            
            # Patient responds
            patient_response = await self._patient_turn(therapist_response)
            self.conversation.add_message(patient_response, "user")
            self._turn_count += 1
            
            if verbose:
                self._display_message(
                    patient_response,
                    self.patient.name,
                    turn=self._turn_count,
                )
            
            previous_stage = stage.value
        
        if verbose:
            self._display_summary()
        
        return self.conversation
    
    def _display_summary(self) -> None:
        """Display a summary of the completed dialogue."""
        table = Table(title="Dialogue Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Session ID", self.conversation.session_id[:8] + "...")
        table.add_row("Patient", f"{self.patient.name} ({self.patient.vignette_name})")
        table.add_row("Total Turns", str(self._turn_count))
        table.add_row("Messages", str(len(self.conversation.messages)))
        table.add_row("Stages Visited", ", ".join(dict.fromkeys(self.conversation.stages)))
        table.add_row("Completed", "Yes" if self._is_complete else "No (max turns)")
        
        console.print()
        console.print(table)
    
    def save_dialogue(
        self,
        output_path: str | Path,
        include_metadata: bool = True,
    ) -> Path:
        """Save the dialogue to a JSON file.
        
        Args:
            output_path: Path for the output file
            include_metadata: Whether to include generation metadata
            
        Returns:
            Path to the saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "session_id": self.conversation.session_id,
            "language": self.language,
            "vignette": self.patient.vignette_name,
            "patient_name": self.patient.name,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "stage": msg.stage,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in self.conversation.messages
            ],
            "stages": self.conversation.stages,
        }
        
        if include_metadata:
            data["metadata"] = {
                "generated_at": datetime.now().isoformat(),
                "total_turns": self._turn_count,
                "completed": self._is_complete,
                "max_turns": self.max_turns,
            }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]Dialogue saved to: {output_path}[/green]")
        return output_path
    
    def get_conversation_summary(self) -> dict[str, Any]:
        """Get a summary of the conversation.
        
        Returns:
            Dictionary with conversation statistics
        """
        return {
            "session_id": self.conversation.session_id,
            "patient": self.patient.name,
            "vignette": self.patient.vignette_name,
            "total_turns": self._turn_count,
            "message_count": len(self.conversation.messages),
            "stages_visited": list(dict.fromkeys(self.conversation.stages)),
            "completed": self._is_complete,
            "language": self.language,
        }


async def run_generation(
    vignette_name: str,
    language: str = "en",
    output_path: str | None = None,
    max_turns: int = 50,
    verbose: bool = True,
) -> Conversation:
    """Convenience function to run dialogue generation.
    
    Args:
        vignette_name: Name of the vignette to use
        language: Session language ("en" or "de")
        output_path: Optional path to save the dialogue
        max_turns: Maximum turns before termination
        verbose: Whether to display rich output
        
    Returns:
        The completed Conversation object
        
    Example:
        >>> conv = await run_generation("anxious", output_path="dialogues/test.json")
    """
    stack = GenerationStack.from_vignette(
        vignette_name,
        language=language,
        max_turns=max_turns,
    )
    
    conversation = await stack.run(verbose=verbose)
    
    if output_path:
        stack.save_dialogue(output_path)
    
    return conversation


def list_available_vignettes() -> list[str]:
    """List all available vignettes for generation.
    
    Returns:
        List of vignette names
    """
    vignettes = list_vignettes()
    
    if vignettes:
        console.print("[bold]Available Vignettes:[/bold]")
        for v in vignettes:
            console.print(f"  - {v}")
    else:
        console.print("[yellow]No vignettes found in data/vignettes/[/yellow]")
    
    return vignettes
