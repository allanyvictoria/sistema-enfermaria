from sqlalchemy import Table, Column, BigInteger, ForeignKey, String
from app.database import Base


turma_professora = Table(
    'turma_professora',
    Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('turma_id', BigInteger, ForeignKey('turma.id')),
    Column('professora_id', BigInteger, ForeignKey('professora.id')),
    Column('papel', String(20))
)
