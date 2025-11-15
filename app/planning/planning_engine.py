# ==============================================================================
# app/planning/planning_engine.py
# The Planning Engine - Fortune 500-Grade Task Planning System
# ==============================================================================
"""
Planning Engine: Cursor-Style Plan-First Workflow

This module transforms CLARITY from a black-box AI into a transparent,
collaborative intelligence partner. Instead of immediately executing tasks,
CLARITY first creates a detailed plan, explains its approach, and waits
for user approval.

This approach:
- Builds trust through transparency
- Allows users to course-correct before execution
- Reduces wasted effort on misunderstood requirements
- Demonstrates professional-grade project management
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import google.generativeai as genai

logger = logging.getLogger(__name__)


@dataclass
class PlanStep:
    """
    A single step in an execution plan.
    
    Attributes:
        step_number: Sequential step number
        title: Short title for the step
        description: Detailed description of what will be done
        rationale: Why this step is necessary
        estimated_time: Estimated time in minutes
        dependencies: List of step numbers that must complete first
        status: Current status ('pending', 'in_progress', 'completed', 'skipped')
        result: Result data after execution
    """
    step_number: int
    title: str
    description: str
    rationale: str
    estimated_time: int = 5
    dependencies: List[int] = field(default_factory=list)
    status: str = 'pending'
    result: Optional[Dict[str, Any]] = None
    

@dataclass
class ExecutionPlan:
    """
    A complete execution plan for a task.
    
    Attributes:
        plan_id: Unique plan identifier
        task_description: Original task description
        task_type: Type of task ('proposal', 'analysis', 'data_entry', etc.)
        approach: High-level approach summary
        steps: List of PlanStep objects
        total_estimated_time: Total estimated time in minutes
        created_at: Plan creation timestamp
        approved: Whether plan was approved by user
        approved_at: Approval timestamp
        completed_steps: Number of completed steps
    """
    plan_id: str
    task_description: str
    task_type: str
    approach: str
    steps: List[PlanStep]
    total_estimated_time: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    approved: bool = False
    approved_at: Optional[datetime] = None
    completed_steps: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary for JSON serialization."""
        return {
            'plan_id': self.plan_id,
            'task_description': self.task_description,
            'task_type': self.task_type,
            'approach': self.approach,
            'steps': [
                {
                    'step_number': step.step_number,
                    'title': step.title,
                    'description': step.description,
                    'rationale': step.rationale,
                    'estimated_time': step.estimated_time,
                    'dependencies': step.dependencies,
                    'status': step.status
                }
                for step in self.steps
            ],
            'total_estimated_time': self.total_estimated_time,
            'created_at': self.created_at.isoformat(),
            'approved': self.approved,
            'completed_steps': self.completed_steps,
            'total_steps': len(self.steps)
        }


class PlanningEngine:
    """
    Planning Engine: Creates detailed execution plans before starting work.
    
    This engine analyzes tasks, breaks them into steps, and presents a
    clear plan to users before execution begins.
    """
    
    def __init__(self):
        """Initialize the Planning Engine."""
        try:
            api_key = os.environ.get('GOOGLE_API_KEY')
            if not api_key:
                logger.error("❌ GOOGLE_API_KEY not set! Planning engine will fail.")
                self.initialized = False
                return
            
            genai.configure(api_key=api_key)
            # Try available models in order of preference
            model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            self.model = None
            self.model_name = None
            
            for model_name in model_names:
                try:
                    test_model = genai.GenerativeModel(model_name)
                    self.model = test_model
                    self.model_name = model_name
                    logger.info(f"✅ PlanningEngine initialized with {model_name}")
                    break
                except Exception as e:
                    logger.debug(f"Model {model_name} not available: {e}")
                    continue
            
            if not self.model:
                raise Exception(f"None of the models are available: {model_names}")
            
            self.initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize PlanningEngine: {e}")
            self.initialized = False
    
    def create_plan(
        self,
        task_description: str,
        task_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        """
        Create an execution plan for a task.
        
        Args:
            task_description: Description of what the user wants to accomplish
            task_type: Type of task ('proposal', 'analysis', 'data_entry', etc.)
            context: Optional context (files, user preferences, etc.)
            
        Returns:
            ExecutionPlan object with detailed steps
        """
        if not self.initialized:
            return self._create_fallback_plan(task_description, task_type)
        
        try:
            # Build planning prompt
            prompt = self._build_planning_prompt(task_description, task_type, context)
            
            # Call LLM to create plan
            response = self.model.generate_content(prompt)
            
            # Parse response into ExecutionPlan
            plan = self._parse_plan_response(
                response.text,
                task_description,
                task_type
            )
            
            logger.info(f"Created plan with {len(plan.steps)} steps for {task_type}")
            
            return plan
            
        except Exception as e:
            logger.error(f"Planning error: {e}", exc_info=True)
            return self._create_fallback_plan(task_description, task_type)
    
    def _build_planning_prompt(
        self,
        task_description: str,
        task_type: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Build a prompt for the LLM to create a plan.
        
        Args:
            task_description: Task description
            task_type: Task type
            context: Optional context
            
        Returns:
            Prompt string
        """
        context_str = ""
        if context:
            if context.get('files'):
                file_count = len(context['files'])
                context_str += f"\n- {file_count} documents provided"
            if context.get('user_tier'):
                context_str += f"\n- User tier: {context['user_tier']}"
        
        prompt = f"""You are CLARITY, a world-class AI planning assistant. Your mission is to create detailed, professional execution plans.

TASK TYPE: {task_type}

TASK DESCRIPTION:
{task_description}

CONTEXT:{context_str if context_str else " None"}

YOUR MISSION: Create a detailed execution plan that breaks this task into clear, actionable steps.

PLANNING REQUIREMENTS:
1. Start with a high-level approach summary (2-3 sentences)
2. Break the task into 3-10 concrete steps
3. For each step, provide:
   - A clear title
   - Detailed description of what will be done
   - Rationale (why this step is necessary)
   - Estimated time in minutes
   - Dependencies (which steps must complete first)

4. Steps should be:
   - Specific and actionable
   - Logically ordered
   - Progressive (each builds on previous)
   - Complete (covers entire task)

5. Consider:
   - Data quality and validation
   - User review points
   - Risk mitigation
   - Time efficiency

Return your plan as valid JSON with this exact structure:
{{
    "approach": "High-level approach summary",
    "steps": [
        {{
            "step_number": 1,
            "title": "Step title",
            "description": "Detailed description",
            "rationale": "Why this step is necessary",
            "estimated_time": 10,
            "dependencies": []
        }},
        ...
    ]
}}

CRITICAL: Return ONLY valid JSON, no markdown formatting or explanations.

BEGIN PLANNING NOW:"""
        
        return prompt
    
    def _parse_plan_response(
        self,
        response_text: str,
        task_description: str,
        task_type: str
    ) -> ExecutionPlan:
        """
        Parse LLM response into an ExecutionPlan.
        
        Args:
            response_text: LLM response
            task_description: Original task description
            task_type: Task type
            
        Returns:
            ExecutionPlan object
        """
        try:
            # Clean response
            cleaned = response_text.strip().replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            parsed = json.loads(cleaned)
            
            # Extract components
            approach = parsed.get('approach', 'Execute task systematically')
            steps_data = parsed.get('steps', [])
            
            # Create PlanStep objects
            steps = []
            total_time = 0
            
            for step_data in steps_data:
                step = PlanStep(
                    step_number=step_data.get('step_number', len(steps) + 1),
                    title=step_data.get('title', f"Step {len(steps) + 1}"),
                    description=step_data.get('description', ''),
                    rationale=step_data.get('rationale', ''),
                    estimated_time=step_data.get('estimated_time', 5),
                    dependencies=step_data.get('dependencies', [])
                )
                steps.append(step)
                total_time += step.estimated_time
            
            # Generate plan ID
            import uuid
            plan_id = str(uuid.uuid4())[:8]
            
            # Create ExecutionPlan
            plan = ExecutionPlan(
                plan_id=plan_id,
                task_description=task_description,
                task_type=task_type,
                approach=approach,
                steps=steps,
                total_estimated_time=total_time
            )
            
            return plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse plan JSON: {e}")
            return self._create_fallback_plan(task_description, task_type)
        
        except Exception as e:
            logger.error(f"Failed to parse plan response: {e}")
            return self._create_fallback_plan(task_description, task_type)
    
    def _create_fallback_plan(
        self,
        task_description: str,
        task_type: str
    ) -> ExecutionPlan:
        """
        Create a basic fallback plan if AI planning fails.
        
        Args:
            task_description: Task description
            task_type: Task type
            
        Returns:
            Basic ExecutionPlan
        """
        import uuid
        
        steps = [
            PlanStep(
                step_number=1,
                title="Analyze Input",
                description="Review and understand all provided documents and requirements",
                rationale="Foundation for accurate execution",
                estimated_time=5
            ),
            PlanStep(
                step_number=2,
                title="Execute Task",
                description=f"Perform the requested {task_type} task",
                rationale="Core task execution",
                estimated_time=15,
                dependencies=[1]
            ),
            PlanStep(
                step_number=3,
                title="Review and Validate",
                description="Verify results meet requirements and quality standards",
                rationale="Ensure accuracy and completeness",
                estimated_time=5,
                dependencies=[2]
            )
        ]
        
        return ExecutionPlan(
            plan_id=str(uuid.uuid4())[:8],
            task_description=task_description,
            task_type=task_type,
            approach="Systematic three-phase approach: analyze, execute, validate",
            steps=steps,
            total_estimated_time=25
        )
    
    def approve_plan(self, plan: ExecutionPlan) -> ExecutionPlan:
        """
        Mark a plan as approved by the user.
        
        Args:
            plan: ExecutionPlan to approve
            
        Returns:
            Updated ExecutionPlan
        """
        plan.approved = True
        plan.approved_at = datetime.utcnow()
        logger.info(f"Plan {plan.plan_id} approved")
        return plan
    
    def execute_step(
        self,
        plan: ExecutionPlan,
        step_number: int,
        executor_function: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a single step in the plan.
        
        Args:
            plan: ExecutionPlan
            step_number: Step number to execute
            executor_function: Function to execute the step
            **kwargs: Arguments for executor function
            
        Returns:
            Dict with execution result
        """
        try:
            # Find step
            step = next((s for s in plan.steps if s.step_number == step_number), None)
            
            if not step:
                return {
                    'success': False,
                    'error': f'Step {step_number} not found'
                }
            
            # Check dependencies
            for dep in step.dependencies:
                dep_step = next((s for s in plan.steps if s.step_number == dep), None)
                if dep_step and dep_step.status != 'completed':
                    return {
                        'success': False,
                        'error': f'Dependency step {dep} not completed'
                    }
            
            # Mark as in progress
            step.status = 'in_progress'
            
            # Execute
            result = executor_function(**kwargs)
            
            # Update step
            step.result = result
            step.status = 'completed' if result.get('success', False) else 'failed'
            
            if step.status == 'completed':
                plan.completed_steps += 1
            
            logger.info(f"Executed step {step_number}: {step.status}")
            
            return result
            
        except Exception as e:
            logger.error(f"Step execution error: {e}", exc_info=True)
            if step:
                step.status = 'failed'
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_plan_status(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Get current status of plan execution.
        
        Args:
            plan: ExecutionPlan
            
        Returns:
            Dict with status information
        """
        total_steps = len(plan.steps)
        completed = sum(1 for s in plan.steps if s.status == 'completed')
        in_progress = sum(1 for s in plan.steps if s.status == 'in_progress')
        failed = sum(1 for s in plan.steps if s.status == 'failed')
        
        progress_percentage = (completed / total_steps * 100) if total_steps > 0 else 0
        
        return {
            'plan_id': plan.plan_id,
            'total_steps': total_steps,
            'completed_steps': completed,
            'in_progress_steps': in_progress,
            'failed_steps': failed,
            'progress_percentage': round(progress_percentage, 1),
            'approved': plan.approved,
            'steps': [
                {
                    'step_number': step.step_number,
                    'title': step.title,
                    'status': step.status
                }
                for step in plan.steps
            ]
        }


# Global instance
_engine = None


def get_planning_engine() -> PlanningEngine:
    """
    Get or create the global PlanningEngine instance.
    
    Returns:
        PlanningEngine instance
    """
    global _engine
    
    if _engine is None:
        _engine = PlanningEngine()
    
    return _engine
