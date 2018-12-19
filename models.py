from peewee import Model, CharField, SqliteDatabase, BooleanField, TextField, \
    ForeignKeyField, DateField

db = SqliteDatabase('storage.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1 * 64000,  # 64MB
    'foreign_keys': 1,
    'ignore_check_constraints': 0})

db.connect()


class BaseModel(Model):
    class Meta:
        database = db


class Author(BaseModel):
    name = CharField(unique=True)
    affiliation = CharField(null=True)
    orcid_id = CharField(null=True)


class Keyword(BaseModel):
    keyword = CharField(unique=True)


class Publication(BaseModel):
    name = CharField(unique=True)


class Doctype(BaseModel):
    name = CharField(unique=True)


class Paper(BaseModel):
    title = TextField()
    abstract = TextField()
    doi = CharField(unique=True)
    bibtex = TextField()
    first_author = ForeignKeyField(Author)
    publication = ForeignKeyField(Publication)
    doctype = ForeignKeyField(Doctype)
    arxiv_identifier = CharField(unique=True)
    bibcode = CharField(unique=True)
    year = CharField()
    pubdate = DateField()
    pdf_downloaded = BooleanField()


class PaperAuthors(BaseModel):
    paper = ForeignKeyField(Paper)
    author = ForeignKeyField(Author)


class PaperKeywords(BaseModel):
    paper = ForeignKeyField(Paper)
    keyword = ForeignKeyField(Keyword)
