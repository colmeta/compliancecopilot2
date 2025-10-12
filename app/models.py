# ==============================================================================
# app/models.py -- The DEFINITIVE AND COMPLETE Version
# This version contains both the User and the APIKey models.
# ==============================================================================

# Imports the ONE TRUE db instance from our app factory package in __init__.py
from . import db

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import secrets

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    api_keys = db.relationship('APIKey', backref='owner', lazy='dynamic')

    def __init__(self, email, password):
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class APIKey(db.Model):
    """The APIKey model for protecting service endpoints."""
    
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    key_hash = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __init__(self, user_id):
        self.user_id = user_id
    
    def check_key(self, key_to_check):
        return check_password_hash(self.key_hash, key_to_check)
        
    @staticmethod
    def generate_key():
        new_key = secrets.token_urlsafe(32)
        hashed_key = generate_password_hash(new_key, method='pbkdf2:sha256')
        return new_key, hashed_key

class AnalysisFeedback(db.Model):
    """User feedback on CLARITY analysis results - The Accountability Layer."""
    
    __tablename__ = 'analysis_feedback'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(256), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 for thumbs up, -1 for thumbs down
    feedback_text = db.Column(db.Text, nullable=True)  # Optional qualitative feedback
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to user
    user = db.relationship('User', backref='feedback_submissions')
    
    def __repr__(self):
        return f'<AnalysisFeedback job_id={self.job_id} rating={self.rating}>'

class FinalizedBriefing(db.Model):
    """User-finalized analysis briefings - The Co-Worker Record."""
    
    __tablename__ = 'finalized_briefings'
    id = db.Column(db.Integer, primary_key=True)
    original_job_id = db.Column(db.String(256), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    final_content = db.Column(db.Text, nullable=False)  # JSON string of edited content
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to user
    user = db.relationship('User', backref='finalized_briefings')
    
    def __repr__(self):
        return f'<FinalizedBriefing job_id={self.original_job_id} user={self.user_id}>'


# ==============================================================================
# PHASE 4: ADVANCED FEATURES - NEW MODELS
# ==============================================================================

# --- Multi-Tier Subscription System ---

class Subscription(db.Model):
    """User subscription tier and status - The Monetization Engine."""
    
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    tier = db.Column(db.String(50), nullable=False, default='free')  # free, pro, enterprise
    status = db.Column(db.String(50), nullable=False, default='active')  # active, cancelled, suspended
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)  # None for active subscriptions
    stripe_customer_id = db.Column(db.String(256), nullable=True)  # For payment processing
    stripe_subscription_id = db.Column(db.String(256), nullable=True)
    
    # Relationship to user
    user = db.relationship('User', backref=db.backref('subscription', uselist=False))
    
    def __repr__(self):
        return f'<Subscription user={self.user_id} tier={self.tier} status={self.status}>'
    
    def is_active(self):
        """Check if subscription is currently active."""
        return self.status == 'active'
    
    def can_use_feature(self, feature_name):
        """Check if user's tier allows access to a specific feature."""
        from app.tiers import TIER_LIMITS
        return TIER_LIMITS.get(self.tier, {}).get(feature_name, False)


class UsageMetrics(db.Model):
    """Track user usage for metered features - The Usage Tracker."""
    
    __tablename__ = 'usage_metrics'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    metric_type = db.Column(db.String(100), nullable=False, index=True)  # documents, analysis, audio_minutes, etc.
    count = db.Column(db.Integer, nullable=False, default=0)
    period = db.Column(db.String(20), nullable=False, index=True)  # YYYY-MM format for monthly tracking
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    metadata = db.Column(db.Text, nullable=True)  # JSON for additional details
    
    # Relationship to user
    user = db.relationship('User', backref='usage_metrics')
    
    def __repr__(self):
        return f'<UsageMetrics user={self.user_id} type={self.metric_type} count={self.count}>'


# --- Collaborative Workspaces ---

class Workspace(db.Model):
    """Shared collaborative workspace - The Team Vault."""
    
    __tablename__ = 'workspaces'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    workspace_type = db.Column(db.String(50), nullable=False, default='team')  # personal, team, organization
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    settings = db.Column(db.Text, nullable=True)  # JSON for workspace settings
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    owner = db.relationship('User', backref='owned_workspaces')
    
    def __repr__(self):
        return f'<Workspace id={self.id} name={self.name} owner={self.owner_id}>'


class WorkspaceMember(db.Model):
    """Workspace membership with roles - The Access Control."""
    
    __tablename__ = 'workspace_members'
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    role = db.Column(db.String(50), nullable=False, default='viewer')  # owner, admin, editor, viewer
    permissions = db.Column(db.Text, nullable=True)  # JSON for granular permissions
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    invited_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    workspace = db.relationship('Workspace', backref='members')
    user = db.relationship('User', foreign_keys=[user_id], backref='workspace_memberships')
    inviter = db.relationship('User', foreign_keys=[invited_by])
    
    # Unique constraint: user can only be a member once per workspace
    __table_args__ = (db.UniqueConstraint('workspace_id', 'user_id', name='unique_workspace_member'),)
    
    def __repr__(self):
        return f'<WorkspaceMember workspace={self.workspace_id} user={self.user_id} role={self.role}>'


class WorkspaceDocument(db.Model):
    """Documents in workspaces - The Shared Knowledge."""
    
    __tablename__ = 'workspace_documents'
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False, index=True)
    document_name = db.Column(db.String(512), nullable=False)
    document_path = db.Column(db.String(1024), nullable=False)  # Path in storage
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    visibility = db.Column(db.String(50), nullable=False, default='workspace')  # workspace, public, private
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    file_size = db.Column(db.Integer, nullable=True)  # Bytes
    file_type = db.Column(db.String(100), nullable=True)
    
    # Relationships
    workspace = db.relationship('Workspace', backref='documents')
    uploader = db.relationship('User', backref='uploaded_documents')
    
    def __repr__(self):
        return f'<WorkspaceDocument id={self.id} workspace={self.workspace_id} name={self.document_name}>'


class DocumentShare(db.Model):
    """Granular document sharing - The Share Control."""
    
    __tablename__ = 'document_shares'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('workspace_documents.id'), nullable=False, index=True)
    shared_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shared_with = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    permissions = db.Column(db.String(50), nullable=False, default='view')  # view, edit, admin
    expires_at = db.Column(db.DateTime, nullable=True)  # None for no expiration
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    access_count = db.Column(db.Integer, default=0, nullable=False)
    last_accessed = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    document = db.relationship('WorkspaceDocument', backref='shares')
    sharer = db.relationship('User', foreign_keys=[shared_by])
    recipient = db.relationship('User', foreign_keys=[shared_with])
    
    def __repr__(self):
        return f'<DocumentShare doc={self.document_id} from={self.shared_by} to={self.shared_with}>'
    
    def is_valid(self):
        """Check if share is still valid (not expired)."""
        if self.expires_at is None:
            return True
        return datetime.utcnow() < self.expires_at


# --- Analytics & Insights ---

class AnalyticsSnapshot(db.Model):
    """Daily analytics snapshots - The Metrics Warehouse."""
    
    __tablename__ = 'analytics_snapshots'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)  # None for system-wide
    date = db.Column(db.Date, nullable=False, index=True)
    metric_name = db.Column(db.String(100), nullable=False, index=True)
    value = db.Column(db.Float, nullable=False)
    metadata = db.Column(db.Text, nullable=True)  # JSON for additional context
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to user
    user = db.relationship('User', backref='analytics_snapshots')
    
    def __repr__(self):
        return f'<AnalyticsSnapshot user={self.user_id} metric={self.metric_name} value={self.value}>'


class DocumentAnalytics(db.Model):
    """Per-document analytics - The Document Intelligence."""
    
    __tablename__ = 'document_analytics'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('workspace_documents.id'), nullable=False, unique=True)
    views = db.Column(db.Integer, default=0, nullable=False)
    analyses = db.Column(db.Integer, default=0, nullable=False)
    shares = db.Column(db.Integer, default=0, nullable=False)
    last_accessed = db.Column(db.DateTime, nullable=True)
    avg_confidence_score = db.Column(db.Float, nullable=True)
    
    # Relationship
    document = db.relationship('WorkspaceDocument', backref=db.backref('analytics', uselist=False))
    
    def __repr__(self):
        return f'<DocumentAnalytics doc={self.document_id} views={self.views} analyses={self.analyses}>'


# --- Enterprise Security & Compliance ---

class AuditLog(db.Model):
    """Complete activity tracking - The Compliance Trail."""
    
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)  # login, upload, download, delete, etc.
    resource_type = db.Column(db.String(100), nullable=True)  # document, workspace, user, etc.
    resource_id = db.Column(db.String(256), nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON for action details
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(512), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default='success')  # success, failure, warning
    
    # Relationship to user
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog user={self.user_id} action={self.action} status={self.status}>'


class ComplianceEvent(db.Model):
    """Compliance-specific events - The Regulatory Tracker."""
    
    __tablename__ = 'compliance_events'
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False, index=True)  # gdpr_export, hipaa_access, data_deletion
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    data_classification = db.Column(db.String(50), nullable=True)  # public, internal, confidential, restricted
    retention_date = db.Column(db.DateTime, nullable=True)  # When data should be deleted
    details = db.Column(db.Text, nullable=True)  # JSON for event details
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    handled = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationship to user
    user = db.relationship('User', backref='compliance_events')
    
    def __repr__(self):
        return f'<ComplianceEvent type={self.event_type} user={self.user_id}>'


class DataRetentionPolicy(db.Model):
    """Configurable data retention - The Retention Manager."""
    
    __tablename__ = 'data_retention_policies'
    id = db.Column(db.Integer, primary_key=True)
    data_type = db.Column(db.String(100), nullable=False, index=True)  # documents, logs, analytics, etc.
    retention_days = db.Column(db.Integer, nullable=False)  # Days to retain data
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # None for system-wide
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='retention_policies')
    workspace = db.relationship('Workspace', backref='retention_policies')
    
    def __repr__(self):
        return f'<DataRetentionPolicy type={self.data_type} days={self.retention_days}>'


class ConsentRecord(db.Model):
    """User consent tracking - The Consent Manager."""
    
    __tablename__ = 'consent_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    consent_type = db.Column(db.String(100), nullable=False, index=True)  # terms, privacy, marketing, data_processing
    granted = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = db.Column(db.String(50), nullable=True)
    consent_text = db.Column(db.Text, nullable=True)  # Version of consent text shown to user
    
    # Relationship to user
    user = db.relationship('User', backref='consent_records')
    
    def __repr__(self):
        return f'<ConsentRecord user={self.user_id} type={self.consent_type} granted={self.granted}>'


# --- AI Optimization ---

class PromptVariant(db.Model):
    """Prompt A/B testing variants - The Prompt Lab."""
    
    __tablename__ = 'prompt_variants'
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(100), nullable=False, index=True)  # legal, financial, security, etc.
    variant_name = db.Column(db.String(100), nullable=False)  # variant_a, variant_b, etc.
    prompt_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationship
    creator = db.relationship('User', backref='prompt_variants')
    
    # Unique constraint: one variant name per domain
    __table_args__ = (db.UniqueConstraint('domain', 'variant_name', name='unique_domain_variant'),)
    
    def __repr__(self):
        return f'<PromptVariant domain={self.domain} variant={self.variant_name}>'


class PromptPerformance(db.Model):
    """Track prompt effectiveness - The Performance Monitor."""
    
    __tablename__ = 'prompt_performance'
    id = db.Column(db.Integer, primary_key=True)
    variant_id = db.Column(db.Integer, db.ForeignKey('prompt_variants.id'), nullable=False, index=True)
    avg_confidence = db.Column(db.Float, nullable=True)
    positive_feedback_ratio = db.Column(db.Float, nullable=True)  # 0.0 to 1.0
    avg_response_time = db.Column(db.Float, nullable=True)  # Seconds
    usage_count = db.Column(db.Integer, default=0, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    variant = db.relationship('PromptVariant', backref=db.backref('performance', uselist=False))
    
    def __repr__(self):
        return f'<PromptPerformance variant={self.variant_id} usage={self.usage_count}>'
