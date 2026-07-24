from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.data_source import DataSource


class DataSourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, data_source_id: int) -> Optional[DataSource]:
        return self.db.query(DataSource).filter(DataSource.id == data_source_id).first()

    def get_all_by_company(self, company_id: int) -> List[DataSource]:
        return self.db.query(DataSource).filter(DataSource.company_id == company_id).all()

    def create(self, data_source: DataSource) -> DataSource:
        self.db.add(data_source)
        self.db.commit()
        self.db.refresh(data_source)
        return data_source