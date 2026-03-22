"""005 create ETESTER module v4 tables

Revision ID: b1c2d3e4f5a6
Revises: a7b8c9d0e1f2
Create Date: 2026-03-21 12:00:00.000000

Creates 7 new tables for the ETESTER module v4.
All FK references point to existing tables (students, milestones, mentors).
No existing columns are altered.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'a7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. etester_core (1:1 with students)
    op.create_table(
        'etester_core',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('student_id', sa.String(length=50), nullable=False),
        sa.Column('academic_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('writing_growth', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('mentor_verifications', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_contributions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('contributor_breakdown', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('pending_trace_links', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('pending_approvals', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('requirements_coverage', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('parent_support_level', sa.String(length=20), nullable=False, server_default='low'),
        sa.Column('parent_engagement_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('institutional_stamp', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('stamped_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stamped_by', sa.Integer(), nullable=True),
        sa.Column('consistency_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('narrative_en', sa.Text(), nullable=True),
        sa.Column('narrative_vn', sa.Text(), nullable=True),
        sa.Column('narrative_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('badge_issued', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['stamped_by'], ['mentors.mentor_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id'),
    )
    op.create_index('idx_etester_core_student', 'etester_core', ['student_id'], unique=True)

    # 2. milestone_trace_links (Approach C linking)
    op.create_table(
        'milestone_trace_links',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('from_milestone_id', sa.Integer(), nullable=False),
        sa.Column('to_milestone_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.String(length=50), nullable=False),
        sa.Column('relationship_type', sa.String(length=30), nullable=False),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('student_context_note', sa.Text(), nullable=True),
        sa.Column('student_noted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('suggested_by_ai', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('confirmed_by_mentor', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('confirmed_by_mentor_id', sa.Integer(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('confidence >= 0.0 AND confidence <= 1.0', name='chk_trace_confidence'),
        sa.CheckConstraint(
            "relationship_type IN ('experience_source', 'revision_of', 'mentor_guided', 'skill_applied', 'score_progression', 'recommends')",
            name='chk_relationship_type',
        ),
        sa.ForeignKeyConstraint(['confirmed_by_mentor_id'], ['mentors.mentor_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['from_milestone_id'], ['milestones.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['to_milestone_id'], ['milestones.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('from_milestone_id', 'to_milestone_id', name='uq_trace_link_pair'),
    )
    op.create_index('idx_trace_links_student', 'milestone_trace_links', ['student_id'])
    op.create_index('idx_trace_links_pending', 'milestone_trace_links', ['student_id', 'confirmed_by_mentor'])

    # 3. milestone_artifacts (hash + 3-stage signing)
    op.create_table(
        'milestone_artifacts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('milestone_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.String(length=50), nullable=False),
        sa.Column('full_text_content', sa.Text(), nullable=True),
        sa.Column('artifact_hash', sa.String(length=64), nullable=True),
        sa.Column('prev_artifact_hash', sa.String(length=64), nullable=True),
        sa.Column('vc_signature', sa.Text(), nullable=True),
        sa.Column('mentor_signed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('admin_signed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('manager_signed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['milestone_id'], ['milestones.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('milestone_id'),
    )
    op.create_index('idx_milestone_artifacts_student', 'milestone_artifacts', ['student_id'])

    # 4. artifact_forms (structured form data)
    op.create_table(
        'artifact_forms',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('milestone_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.String(length=50), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('form_version', sa.String(length=10), nullable=False, server_default='1.0'),
        sa.Column('form_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('blooms_level', sa.String(length=30), nullable=True),
        sa.Column('skills_practiced', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('had_leadership_role', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('leadership_role_title', sa.String(length=255), nullable=True),
        sa.Column('leadership_team_size', sa.Integer(), nullable=True),
        sa.Column('leadership_outcome', sa.String(length=500), nullable=True),
        sa.Column('mentor_comment', sa.Text(), nullable=True),
        sa.Column('mentor_comment_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['mentor_comment_by'], ['mentors.mentor_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['milestone_id'], ['milestones.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('milestone_id'),
    )
    op.create_index('idx_artifact_forms_student', 'artifact_forms', ['student_id'])

    # 5. mentor_verifications (append-only audit log)
    op.create_table(
        'mentor_verifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('milestone_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.String(length=50), nullable=False),
        sa.Column('verifier_id', sa.Integer(), nullable=False),
        sa.Column('verifier_type', sa.String(length=20), nullable=False),
        sa.Column('action_type', sa.String(length=30), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('trace_link_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['milestone_id'], ['milestones.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trace_link_id'], ['milestone_trace_links.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_mentor_verif_student', 'mentor_verifications', ['student_id'])
    op.create_index('idx_mentor_verif_milestone', 'mentor_verifications', ['milestone_id'])

    # 6. auth_scoring_results (7-dimension scoring)
    op.create_table(
        'auth_scoring_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('milestone_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.String(length=50), nullable=False),
        sa.Column('auth_score', sa.Integer(), nullable=False),
        sa.Column('verdict', sa.String(length=30), nullable=False),
        sa.Column('dimension_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('explaining_artifacts', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('explanation_en', sa.Text(), nullable=True),
        sa.Column('explanation_vn', sa.Text(), nullable=True),
        sa.Column('graph_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('scored_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['milestone_id'], ['milestones.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_auth_scoring_student', 'auth_scoring_results', ['student_id'])
    op.create_index('idx_auth_scoring_milestone', 'auth_scoring_results', ['milestone_id'])

    # 7. etester_badges (issued credential)
    op.create_table(
        'etester_badges',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('core_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.String(length=50), nullable=False),
        sa.Column('badge_uid', sa.String(length=50), nullable=False),
        sa.Column('credential_type', sa.String(length=30), nullable=False, server_default='jwt_rs256'),
        sa.Column('signed_token', sa.Text(), nullable=False),
        sa.Column('issuer_did', sa.String(length=100), nullable=False, server_default='did:web:etest.edu.vn'),
        sa.Column('badge_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoke_reason', sa.Text(), nullable=True),
        sa.Column('verify_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['core_id'], ['etester_core.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('core_id'),
        sa.UniqueConstraint('badge_uid'),
    )
    op.create_index('idx_etester_badges_student', 'etester_badges', ['student_id'])


    # Seed etester_core for every existing student (auto-populate from students table)
    op.execute("""
        INSERT INTO etester_core (
            student_id, skills, mentor_verifications, total_contributions,
            contributor_breakdown, pending_trace_links, pending_approvals,
            requirements_coverage, parent_support_level, parent_engagement_count,
            institutional_stamp, consistency_score, badge_issued,
            created_at, updated_at
        )
        SELECT
            student_id,
            '[]'::jsonb,
            0, 0,
            '{}'::jsonb,
            0, 0,
            '{}'::jsonb,
            'low',
            0,
            false,
            0,
            false,
            now(), now()
        FROM students
        ON CONFLICT (student_id) DO NOTHING
    """)


def downgrade() -> None:
    op.drop_table('etester_badges')
    op.drop_table('auth_scoring_results')
    op.drop_table('mentor_verifications')
    op.drop_table('artifact_forms')
    op.drop_table('milestone_artifacts')
    op.drop_table('milestone_trace_links')
    op.drop_table('etester_core')
