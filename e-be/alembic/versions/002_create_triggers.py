"""create triggers

Revision ID: 002
Revises: 036a1db07894
Create Date: 2026-03-21

Creates the PostgreSQL trigger that maintains pre-aggregated digest columns
on students whenever milestones change.
"""

from alembic import op

revision = "002"
down_revision = "036a1db07894"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE FUNCTION sync_student_digest_from_milestones()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_sid      VARCHAR(50);
            v_completed BIGINT;
            v_total     BIGINT;
            v_progress  SMALLINT;
            v_next      RECORD;
        BEGIN
            IF TG_OP = 'DELETE' THEN
                v_sid := OLD.student_id;
            ELSE
                v_sid := NEW.student_id;
            END IF;

            SELECT
                COUNT(*) FILTER (WHERE status = 'completed'),
                COUNT(*)
            INTO v_completed, v_total
            FROM milestones WHERE student_id = v_sid;

            IF v_total > 0 THEN
                v_progress := LEAST(100, (v_completed * 100) / v_total);
            ELSE
                v_progress := 0;
            END IF;

            SELECT date, title INTO v_next
            FROM milestones
            WHERE student_id = v_sid
              AND status = 'upcoming'
              AND date >= CURRENT_DATE
            ORDER BY date ASC LIMIT 1;

            UPDATE students SET
                milestones_done      = v_completed,
                progress_pct        = v_progress,
                next_deadline       = v_next.date,
                next_deadline_label = v_next.title,
                days_left          = CASE WHEN v_next.date IS NOT NULL
                                     THEN (v_next.date - CURRENT_DATE)::SMALLINT
                                     ELSE NULL END,
                priority_action     = CASE WHEN v_next.title IS NOT NULL
                                     THEN 'Hoan thanh: ' || v_next.title
                                     ELSE NULL END
            WHERE student_id = v_sid;

            RETURN COALESCE(NEW, OLD);
        END;
        $$;
    """)

    op.execute("""
        CREATE TRIGGER trg_milestones_sync_digest
            AFTER INSERT OR UPDATE OR DELETE ON milestones
            FOR EACH ROW
            EXECUTE FUNCTION sync_student_digest_from_milestones();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_milestones_sync_digest ON milestones;")
    op.execute("DROP FUNCTION IF EXISTS sync_student_digest_from_milestones();")
