"""update_predictions_table_sprint12

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-27 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('predictions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('storm_id', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('storm_name', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('observation_time', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('model_name', sa.String(length=100), server_default='CycloneGuard-RI-Multimodal-TS-Final', nullable=False))
        batch_op.add_column(sa.Column('model_version', sa.String(length=50), server_default='v3.0.0-frozen', nullable=False))
        batch_op.add_column(sa.Column('ri_risk_index', sa.Float(), server_default='0.0', nullable=False))
        batch_op.add_column(sa.Column('operating_threshold', sa.Float(), server_default='0.125', nullable=False))
        batch_op.add_column(sa.Column('ri_flag', sa.Boolean(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('risk_category', sa.String(length=30), server_default='LOW_RISK', nullable=False))
        batch_op.add_column(sa.Column('forecast_horizon_hours', sa.Float(), server_default='24.0', nullable=False))
        batch_op.add_column(sa.Column('temporal_evidence_available', sa.Boolean(), server_default='1', nullable=False))
        batch_op.add_column(sa.Column('satellite_evidence_available', sa.Boolean(), server_default='1', nullable=False))
        batch_op.add_column(sa.Column('satellite_channels', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('input_provenance', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('requested_by', sa.String(length=100), nullable=True))

        batch_op.create_index(batch_op.f('ix_predictions_storm_id'), ['storm_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_predictions_storm_name'), ['storm_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_predictions_model_version'), ['model_version'], unique=False)
        batch_op.create_index(batch_op.f('ix_predictions_risk_category'), ['risk_category'], unique=False)
        batch_op.create_index(batch_op.f('ix_predictions_observation_time'), ['observation_time'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('predictions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_predictions_observation_time'))
        batch_op.drop_index(batch_op.f('ix_predictions_risk_category'))
        batch_op.drop_index(batch_op.f('ix_predictions_model_version'))
        batch_op.drop_index(batch_op.f('ix_predictions_storm_name'))
        batch_op.drop_index(batch_op.f('ix_predictions_storm_id'))

        batch_op.drop_column('requested_by')
        batch_op.drop_column('input_provenance')
        batch_op.drop_column('satellite_channels')
        batch_op.drop_column('satellite_evidence_available')
        batch_op.drop_column('temporal_evidence_available')
        batch_op.drop_column('forecast_horizon_hours')
        batch_op.drop_column('risk_category')
        batch_op.drop_column('ri_flag')
        batch_op.drop_column('operating_threshold')
        batch_op.drop_column('ri_risk_index')
        batch_op.drop_column('model_version')
        batch_op.drop_column('model_name')
        batch_op.drop_column('observation_time')
        batch_op.drop_column('storm_name')
        batch_op.drop_column('storm_id')
