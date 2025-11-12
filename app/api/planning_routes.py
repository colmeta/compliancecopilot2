"""
Planning Engine API Routes - Ask/Plan/Agent Modes
Provides endpoints for creating plans, approving plans, and executing in agent mode
"""

from flask import Blueprint, jsonify, request
import uuid
from datetime import datetime
import logging
from app.planning.planning_engine import get_planning_engine, ExecutionPlan, PlanStep

logger = logging.getLogger(__name__)

planning = Blueprint('planning', __name__, url_prefix='/api/planning')


@planning.route('/create-plan', methods=['POST'])
def create_plan():
    """
    Create an execution plan for a task (Plan mode).
    
    POST /api/planning/create-plan
    Body: {
        "task_description": "Analyze this contract for liability risks",
        "task_type": "analysis",
        "domain": "legal",
        "context": {
            "files": [...],
            "user_tier": "free"
        }
    }
    
    Returns:
        {
            "success": true,
            "plan": {
                "plan_id": "...",
                "approach": "...",
                "steps": [...],
                "total_estimated_time": 30
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        task_description = data.get('task_description', '').strip()
        task_type = data.get('task_type', 'analysis')
        domain = data.get('domain', 'general')
        context = data.get('context', {})
        
        if not task_description:
            return jsonify({'error': 'task_description is required'}), 400
        
        # Add domain to context
        context['domain'] = domain
        
        # Create plan
        engine = get_planning_engine()
        plan = engine.create_plan(
            task_description=task_description,
            task_type=task_type,
            context=context
        )
        
        return jsonify({
            'success': True,
            'plan': plan.to_dict(),
            'message': f'Created plan with {len(plan.steps)} steps'
        }), 200
        
    except Exception as e:
        logger.error(f"Plan creation failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@planning.route('/approve-plan', methods=['POST'])
def approve_plan():
    """
    Approve a plan for execution.
    
    POST /api/planning/approve-plan
    Body: {
        "plan_id": "...",
        "plan": {...}  # Full plan object
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        plan_data = data.get('plan', {})
        plan_id = data.get('plan_id') or plan_data.get('plan_id')
        
        if not plan_id:
            return jsonify({'error': 'plan_id is required'}), 400
        
        # Reconstruct plan from data
        plan = _reconstruct_plan(plan_data)
        
        # Approve
        engine = get_planning_engine()
        approved_plan = engine.approve_plan(plan)
        
        return jsonify({
            'success': True,
            'plan': approved_plan.to_dict(),
            'message': 'Plan approved and ready for execution'
        }), 200
        
    except Exception as e:
        logger.error(f"Plan approval failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@planning.route('/execute-plan', methods=['POST'])
def execute_plan():
    """
    Execute a plan step-by-step (Agent mode).
    
    POST /api/planning/execute-plan
    Body: {
        "plan": {...},  # Full plan object
        "mode": "agent",  # "agent" for autonomous, "manual" for step-by-step
        "auto_approve": true  # Auto-approve each step in agent mode
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        plan_data = data.get('plan', {})
        mode = data.get('mode', 'agent')
        auto_approve = data.get('auto_approve', mode == 'agent')
        
        # Reconstruct plan
        plan = _reconstruct_plan(plan_data)
        
        if not plan.approved and not auto_approve:
            return jsonify({
                'success': False,
                'error': 'Plan must be approved before execution',
                'requires_approval': True
            }), 400
        
        # Auto-approve if in agent mode
        if auto_approve and not plan.approved:
            engine = get_planning_engine()
            plan = engine.approve_plan(plan)
        
        # Execute plan
        engine = get_planning_engine()
        execution_results = []
        
        # Sort steps by dependencies
        sorted_steps = _sort_steps_by_dependencies(plan.steps)
        
        for step in sorted_steps:
            if step.status == 'completed':
                continue
            
            # Execute step (in agent mode, this would call actual execution functions)
            step_result = _execute_step_agent(step, plan, data.get('context', {}))
            execution_results.append({
                'step_number': step.step_number,
                'title': step.title,
                'status': step.status,
                'result': step_result
            })
            
            # In agent mode, continue automatically
            # In manual mode, would wait for user approval
            if step.status == 'failed' and not auto_approve:
                break
        
        # Get final status
        status = engine.get_plan_status(plan)
        
        return jsonify({
            'success': True,
            'plan': plan.to_dict(),
            'execution_results': execution_results,
            'status': status,
            'completed': status['completed_steps'] == status['total_steps']
        }), 200
        
    except Exception as e:
        logger.error(f"Plan execution failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@planning.route('/plan-status/<plan_id>', methods=['GET'])
def get_plan_status(plan_id):
    """
    Get status of a plan execution.
    
    GET /api/planning/plan-status/<plan_id>
    """
    try:
        # In a real implementation, you'd store plans in a database
        # For now, return a message that plan needs to be provided
        return jsonify({
            'success': False,
            'error': 'Plan status requires plan object. Use execute-plan endpoint.',
            'note': 'Plans are currently session-based. Store plan_id and plan object on client side.'
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _reconstruct_plan(plan_data: dict) -> ExecutionPlan:
    """Reconstruct ExecutionPlan from dictionary."""
    steps = []
    for step_data in plan_data.get('steps', []):
        step = PlanStep(
            step_number=step_data.get('step_number', len(steps) + 1),
            title=step_data.get('title', ''),
            description=step_data.get('description', ''),
            rationale=step_data.get('rationale', ''),
            estimated_time=step_data.get('estimated_time', 5),
            dependencies=step_data.get('dependencies', []),
            status=step_data.get('status', 'pending')
        )
        steps.append(step)
    
    plan = ExecutionPlan(
        plan_id=plan_data.get('plan_id', str(uuid.uuid4())[:8]),
        task_description=plan_data.get('task_description', ''),
        task_type=plan_data.get('task_type', 'analysis'),
        approach=plan_data.get('approach', ''),
        steps=steps,
        total_estimated_time=plan_data.get('total_estimated_time', 0),
        approved=plan_data.get('approved', False),
        completed_steps=plan_data.get('completed_steps', 0)
    )
    
    return plan


def _sort_steps_by_dependencies(steps: list) -> list:
    """Sort steps respecting dependencies."""
    sorted_steps = []
    remaining = steps.copy()
    completed_numbers = set()
    
    while remaining:
        progress = False
        for step in remaining[:]:
            # Check if all dependencies are completed
            if all(dep in completed_numbers for dep in step.dependencies):
                sorted_steps.append(step)
                remaining.remove(step)
                completed_numbers.add(step.step_number)
                progress = True
        
        if not progress:
            # Circular dependency or missing step - add remaining
            sorted_steps.extend(remaining)
            break
    
    return sorted_steps


def _execute_step_agent(step: PlanStep, plan: ExecutionPlan, context: dict) -> dict:
    """
    Execute a step in agent mode.
    This would integrate with actual analysis/execution functions.
    """
    try:
        # Mark as in progress
        step.status = 'in_progress'
        
        # Based on step title/description, determine what to execute
        # This is a simplified version - in production, you'd have a mapping
        # of step types to execution functions
        
        task_type = plan.task_type
        domain = context.get('domain', 'general')
        
        # Simulate execution (in production, call actual functions)
        # For now, return success
        result = {
            'success': True,
            'step_number': step.step_number,
            'message': f'Step "{step.title}" executed successfully',
            'output': f'Completed: {step.description}'
        }
        
        step.result = result
        step.status = 'completed'
        plan.completed_steps += 1
        
        logger.info(f"Agent executed step {step.step_number}: {step.title}")
        
        return result
        
    except Exception as e:
        logger.error(f"Step execution error: {e}")
        step.status = 'failed'
        step.result = {'success': False, 'error': str(e)}
        return step.result

