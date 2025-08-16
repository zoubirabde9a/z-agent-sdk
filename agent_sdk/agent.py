from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Agent:
    """Agent definition with instructions and tools.
    
    An Agent represents an LLM-powered assistant with specific instructions
    and a set of tools it can use to accomplish tasks.
    
    Attributes:
        name: Agent identifier
        instructions: System prompt/instructions for the agent
        tools: List of tool functions available to the agent
        handoff_description: Optional description for agent handoff scenarios
    """
    name: str
    instructions: str
    tools: List[Callable[..., Any]] = field(default_factory=list)
    handoff_description: Optional[str] = None

    def tool_specs(self) -> List[Dict[str, Any]]:
        """Get OpenAI-compatible tool specifications.
        
        Returns:
            List of tool specifications in the format expected by OpenAI API
        """
        specs: List[Dict[str, Any]] = []
        for t in self.tools:
            spec = getattr(t, "_tool_spec", None)
            if spec:
                specs.append(spec)
        return specs

    def tool_map(self) -> Dict[str, Callable[..., Any]]:
        """Get mapping from tool names to their implementations.
        
        Returns:
            Dictionary mapping tool names to their function implementations
        """
        mapping: Dict[str, Callable[..., Any]] = {}
        for t in self.tools:
            mapping[t.__name__] = t
        return mapping
