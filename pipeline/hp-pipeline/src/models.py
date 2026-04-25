"""Pydantic models for typed data flowing through the pipeline."""
from typing import Optional
from pydantic import BaseModel, Field


class Task(BaseModel):
    """A single HP task as input to the pipeline."""
    id: str
    delprov: str  # XYZ, KVA, NOG, DTK, ORD, MEK, LÄS, ELF
    year: int
    term: str  # 'vt' or 'ht'
    pass_number: int
    task_number: int
    uppgift_text: str
    answer_options: dict[str, str]  # {"A": "...", "B": "...", ...}
    correct_answer: str


class TaskDescription(BaseModel):
    """Step 1 output: free-text description of what a task tests."""
    task_id: str
    delprov: str
    description: str  # what the task tests, the trap, the strategy
    primary_skill_guess: str  # tentative skill name (in Swedish, lowercase, snake_case)
    requires_image: bool = False
    notes: str = ""


class Cluster(BaseModel):
    """Step 2 output: a group of similar task descriptions."""
    cluster_id: str
    title: str  # short Swedish phrase
    description: str  # what unifies these tasks
    delprov: str  # which delprov this cluster belongs to
    member_task_ids: list[str]


class TaxonomyNode(BaseModel):
    """A node in the hierarchical taxonomy."""
    id: str
    name: str  # display name in Swedish
    level: int  # 1=delprov, 2=area, 3=micro-skill
    parent_id: Optional[str] = None
    description: str
    related_clusters: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)  # other node ids


class Taxonomy(BaseModel):
    """Step 3 output: the full hierarchical taxonomy."""
    nodes: list[TaxonomyNode]
    
    def get_micro_skills(self) -> list[TaxonomyNode]:
        return [n for n in self.nodes if n.level == 3]


class Classification(BaseModel):
    """Step 4 output: a task tagged against the final taxonomy."""
    task_id: str
    primary_skill_id: str
    secondary_skill_ids: list[str] = Field(default_factory=list)
    estimated_difficulty: int = Field(ge=1, le=5)  # 1=easy, 5=hard
    estimated_time_seconds: int
    common_traps: list[str] = Field(default_factory=list)
    solution_strategies: list[str] = Field(default_factory=list)
    classifier_confidence: float = Field(ge=0.0, le=1.0)
    classifier_notes: str = ""
