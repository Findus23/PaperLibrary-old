import math

import ads
import ads.config
import click
import peewee
import requests
from peewee import Model

import config
from models import Author, Keyword, Publication, Doctype, Paper, PaperAuthors, PaperKeywords, db

ads.config.token = config.ads_token


@click.group()
@click.version_option('1.0')
@click.pass_context
def cli(ctx):
    pass
    # print("bla")


cli = cli  # type:click.core.Group


@cli.command()
def init():
    print("initializing")
    db.create_tables([Author, Keyword, Publication, Doctype, Paper, PaperAuthors, PaperKeywords])


# @cli.command()
# @click.argument('file', type=click.Path(exists=True, readable=True))
# @click.option('-p', '--python_file', is_flag=True)
# def add(file, python_file):
#     fo = Files(filename=file, pythonfile=python_file)
#     fo.save()
#     print(file, python_file)
#     pass

@cli.command()
@click.argument("search_query")
@click.option("-a", "--author")
@click.option("-t", "--title")
def add(search_query, author, title):
    fl = ['id', 'author', 'first_author', 'bibcode', 'id', 'year', 'title', 'abstract', 'doi', 'pubdate', "pub",
          "doctype", "identifier"]
    if author:
        search_query += "author:" + author
    if title:
        search_query += "title:" + title
    papers = list(ads.SearchQuery(q=search_query, fl=fl))
    if len(papers) == 0:
        selection = ads.search.Article
        exit()
    elif len(papers) == 1:
        selection = papers[0]  # type:ads.search.Article
    else:
        # first_ten = itertools.islice(papers, 10)
        first_ten = papers[:10]
        single_paper: ads.search.Article
        for index, single_paper in enumerate(first_ten):
            print(index, single_paper.title[0])
        selected_index = click.prompt('select paper', type=int)
        selection = papers[selected_index]  # type:ads.search.Article

    assert len(selection.doi) == 1
    doi = selection.doi[0]

    try:

        paper = Paper.get(Paper.doi == doi)
        print("this paper has already been added")
        exit(1)

    except peewee.DoesNotExist:
        pass

    print("fetching bibcode")
    q = ads.ExportQuery([selection.bibcode])
    bibtex = q.execute()

    print("saving in db")

    paper = Paper()
    assert len(selection.title) == 1
    paper.doi = doi
    paper.title = selection.title[0]
    paper.abstract = selection.abstract
    paper.bibcode = selection.bibcode
    paper.year = selection.year
    paper.pubdate = selection.pubdate
    paper.pdf_downloaded = False
    authors = [Author.get_or_create(name=name)[0] for name in selection.author]
    paper.first_author = Author.get_or_create(name=selection.first_author)[0]
    paper.publication = Publication.get_or_create(name=selection.pub)[0]
    paper.doctype = Doctype.get_or_create(name=selection.doctype)[0]
    paper.arxiv_identifier = [ident for ident in selection.identifier if "arXiv:" in ident][0].split("arXiv:")[-1]
    paper.bibtex = bibtex
    paper.save()
    for author in db.batch_commit(authors, 100):
        PaperAuthors.create(author=author, paper=paper)
    print("fetching PDF")
    arxiv_url = "https://arxiv.org/pdf/{id}".format(id=paper.arxiv_identifier)
    r = requests.get(arxiv_url, stream=True)
    print(arxiv_url)
    with open('library/{filename}.pdf'.format(filename=paper.id), 'wb') as f:
        chunk_size = 1024  # bytes
        file_size = int(r.headers.get('content-length', 0))
        progress_length = math.ceil(file_size // chunk_size)
        with click.progressbar(r.iter_content(chunk_size=20), length=progress_length) as progress_chunks:
            for chunk in progress_chunks:
                f.write(chunk)
    paper.pdf_downloaded = True
    paper.save()


if __name__ == '__main__':
    cli()
